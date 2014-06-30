# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationFormUniqueEmail
from datawinners.accountmanagement.helper import get_trial_account_user_phone_numbers, get_unique_mobile_number_validator
from datawinners.accountmanagement.models import get_data_senders_on_trial_account_with_mobile_number
from datawinners.entity.fields import PhoneNumberField
from mangrove.errors.MangroveException import AccountExpiredException
from models import  Organization
from django.contrib.auth.models import User
from django_countries.countries import  COUNTRIES
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template import Context, loader
from django.utils.http import int_to_base36

def get_organization_sectors():
    return (('', _('Please Select...')),
            ('CommercialBusiness', _('Commercial Business')),
            ('Education', _('Education')),
            ('Finance', _('Finance')),
            ('FoodSecurity', _('Food Security')),
            ('Health', _('Health')),
            ('HumanRights', _('Human Rights')),
            ('Shelter', _('Shelter')),
            ('WaterSanitation', _('Water and Sanitation')),
            ('Other', _('Other')))


def get_country_list():
    return (('', _('Please Select...')),) + tuple(sorted(COUNTRIES, key=lambda (k, v): (v, k)))


class OrganizationForm(ModelForm):
    required_css_class = 'required'
    name = forms.CharField(required=True, label=_('Organization name'))
    sector = forms.CharField(required=False, widget=(
        forms.Select(attrs={'class': 'width-200px'}, choices=get_organization_sectors())),
        label=_('Organization Sector'))
    address = forms.CharField(required=True, max_length=30, label=_('Address'))
    city = forms.CharField(max_length=30, required=True, label=_('City'))
    state = forms.CharField(max_length=30, required=False, label=_('State / Province'))
    country = forms.CharField(required=True, widget=(
        forms.Select(attrs={'class': 'width-200px', 'disabled':'disabled'}, choices=get_country_list())),
        label=_('Country'))
    zipcode = forms.CharField(max_length=30, required=True, label=_('Postal / Zip Code'))
    office_phone = PhoneNumberField(required=False, label=_("Office Phone Number"))
    website = forms.URLField(required=False, label=_('Website'))

    class Meta:
        model = Organization
        exclude = ('in_trial_mode', 'active_date', 'is_deactivate_email_sent', 'addressline2', 'language', 'status',
                   'status_changed_datetime')


    def update(self):
        if self.is_valid():
            self.save()

        return self


class UserProfileForm(forms.Form):
    required_css_class = 'required'

    title = forms.CharField(max_length=30, required=False, label=_("Job title"))
    full_name = forms.CharField(max_length=80, required=True, label=_('Name'))
    username = forms.EmailField(max_length=75, required=True, label=_("Email"), error_messages={
        'invalid': _('Enter a valid email address. Example:name@organization.com')})
    mobile_phone = PhoneNumberField(required=True, label=_("Phone Number"))

    def __init__(self, organization=None, *args, **kwargs):
        self.organization = organization
        forms.Form.__init__(self, *args, **kwargs)

    def clean_mobile_phone(self):
        mobile_number = self.cleaned_data.get('mobile_phone')
        validator = get_unique_mobile_number_validator(self.organization)
        if not validator(self.organization, mobile_number):
            raise ValidationError(_("This phone number is already in use. Please supply a different phone number"))
        return self.cleaned_data.get('mobile_phone')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).count() > 0:
            raise ValidationError(_("This email address is already in use. Please supply a different email address"))
        return self.cleaned_data.get('username').lower()


class EditUserProfileForm(UserProfileForm):
    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)

    def clean_mobile_phone(self):
        return self.cleaned_data.get('mobile_phone')

    def clean_username(self):
        return self.cleaned_data.get('username')


class MinimalRegistrationForm(RegistrationFormUniqueEmail):
    required_css_class = 'required'

    title = forms.CharField(label=_("Job title"), max_length=30, required=False)
    email = forms.EmailField(widget=forms.TextInput(attrs=dict({'class': 'required'},
        maxlength=75)),
        label=_("Email address"),
        error_messages={
            'invalid': _('Enter a valid email address. Example:name@organization.com')})
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(render_value=False),
        label=_("Password"), min_length=6)
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(render_value=False),
        label=_("Password (again)"))

    full_name = forms.CharField(max_length=30, required=True, label=_('Name'))
    mobile_phone = PhoneNumberField(required=True, label=_("Mobile Phone Number"))
    organization_name = forms.CharField(required=True, max_length=30, label=_('Organization Name'))
    organization_sector = forms.CharField(required=False, widget=(
        forms.Select(attrs={'class': 'width-200px'}, choices=get_organization_sectors())),
        label=_('Organization Sector'))
    organization_country = forms.CharField(required=True, widget=(
        forms.Select(attrs={'class': 'width-200px'}, choices=get_country_list())),
        label=_('Country'))
    organization_city = forms.CharField(max_length=30, required=True, label=_('City'))
    username = forms.CharField(max_length=30, required=False)
    language = forms.CharField(widget=forms.HiddenInput(), max_length=2, initial=_("en"))

    def clean_mobile_phone(self):
        mobile_number = self.cleaned_data.get('mobile_phone')
        if get_data_senders_on_trial_account_with_mobile_number(mobile_number).count() > 0 or\
           mobile_number in get_trial_account_user_phone_numbers():
            raise ValidationError(_("This phone number is already in use. Please supply a different phone number"))
        return self.cleaned_data.get('mobile_phone')

    def clean_email(self):
        email = super(MinimalRegistrationForm, self).clean_email()
        return email.lower()

    def strip_and_validate(self, field_name):
        if self.cleaned_data.get(field_name):
            self.cleaned_data[field_name] = self.cleaned_data.get(field_name).strip()
            if self.cleaned_data.get(field_name) == "":
                self._errors[field_name] = self.error_class([self.fields[field_name].error_messages['required']])

    def clean(self):
        for field_name in ['full_name', 'organization_name', 'organization_city']:
            self.strip_and_validate(field_name)
            
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                msg = _("The two password fields didn't match.")
                self._errors['password1'] = self.error_class([msg])
            else:
                if self.cleaned_data['password1'] != self.cleaned_data['password1'].strip():
                    msg = _("There should not be any space at the beginning and the end of the password.")
                    self._errors['password1'] = self.error_class([msg])
        return self.cleaned_data

def payment_details_form():
    pay_monthly = ('pay_monthly', _(mark_safe("pay_monthly_subtitle")))
    pay_half_yearly = ('half_yearly', _(mark_safe("half_yearly_subtitle")))
    pay_yearly = ('yearly', _(mark_safe("yearly_subtitle")))


    INVOICE_PERIOD_CHOICES = (pay_monthly, pay_half_yearly, pay_yearly)

    wire_transfer = ('wire_transfer', _(mark_safe("<div class='radio_title'>Wire transfer</div>")))
    credit_card = ('credit_card', _(mark_safe(
        "<div class='radio_title'>Credit card</div><div class='subtitle_for_radio_button credit_card'></div>")))
    pay_via_ach = ('pay_via_ach', _(mark_safe(
        "<div class='radio_title'>Pay via ACH</div><div class='subtitle_for_radio_button pay_via_ach'></div>")))
    PREFERRED_PAYMENT_CHOICES = (wire_transfer, credit_card, pay_via_ach)
    pro_account = ('Pro', _(mark_safe("pro_subtitle")))
    pro_sms_account = ('Pro SMS', _(mark_safe("pro_sms_subtitle")))
    ACCOUNT_TYPE_CHOICES = (pro_account, pro_sms_account)
    account_type = forms.ChoiceField(required=True, label=_("Account Type"), widget=forms.RadioSelect,
        choices=ACCOUNT_TYPE_CHOICES)
    invoice_period = forms.ChoiceField(required=True, label=_('Invoice Period'), widget=forms.RadioSelect,
        choices=INVOICE_PERIOD_CHOICES, help_text="O, no, Help")

    preferred_payment = forms.ChoiceField(required=False, label=_('Preferred Payment'), widget=forms.RadioSelect,
        choices=PREFERRED_PAYMENT_CHOICES, initial=False)

    return account_type, invoice_period, preferred_payment


class FullRegistrationForm(MinimalRegistrationForm):
    organization_address = forms.CharField(required=True, max_length=30, label=_('Address'))
    organization_addressline2 = forms.CharField(required=False, max_length=30, label=_('Address line 2'))
    organization_state = forms.CharField(max_length=30, required=False, label=_('State / Province'))
    organization_zipcode = forms.RegexField(required=True, max_length=30, regex="^[a-zA-Z\d-]*$",
        error_message=_("Please enter a valid Postal / Zip code"),
        label=_('Postal / Zip Code'))
    organization_office_phone = PhoneNumberField(required=False, label=_("Office Phone Number"))
    organization_website = forms.URLField(required=False, label=_('Website'))

    account_type, invoice_period, preferred_payment = payment_details_form()

    def clean_mobile_phone(self):
        return self.cleaned_data['mobile_phone']


class LoginForm(AuthenticationForm):
    required_css_class = 'required'
    username = forms.CharField(label=_("Username"), max_length=75)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        self.cleaned_data['username'] = username
        return self.cleaned_data['username'].lower()

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        self.check_for_username_and_password(password, username)
        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_username_and_password(self, password, username):
        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Please enter a correct email and password."))
            
            profile = self.user_cache.get_profile()
            organization = Organization.objects.get(org_id=profile.org_id)
            if organization.is_expired():
                raise forms.ValidationError("The trial period is expired")

            if organization.status == 'Deactivated':
                raise forms.ValidationError(_(mark_safe("Your account has been deactivated. Please contact the datawinners support at <a href='mailto:support@datawinners.com'>support@datawinners.com</a> for reactivation of the account.")))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive."))


    def check_trial_account_expired(self):
        org = Organization.objects.get(org_id=self.user_cache.get_profile().org_id)
        if org.is_expired():
            raise AccountExpiredException()


class ResetPasswordForm(PasswordResetForm):
    required_css_class = 'required'

class PasswordSetForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput, min_length=6)
    required_css_class = 'required'

    def clean_new_password1(self):
        cleaned_pwd = self.cleaned_data.get("new_password1")
        if cleaned_pwd != cleaned_pwd.strip():
            raise forms.ValidationError(_("There should not be any space at the beginning and the end of the password."))
        return cleaned_pwd.strip()


class UpgradeForm(forms.Form):
    account_type, invoice_period, preferred_payment = payment_details_form()

class ProRegistrationForm(FullRegistrationForm):
    def __init__(self, *args, **kwargs):
        super(ProRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['account_type'].initial = 'Pro'

class ProSMSRegistrationForm(FullRegistrationForm):
    def __init__(self, *args, **kwargs):
        super(ProSMSRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['account_type'].initial = 'Pro SMS'



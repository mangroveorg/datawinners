# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationFormUniqueEmail
from models import  Organization
from django.contrib.auth.models import User


class OrganizationForm(ModelForm):
    required_css_class = 'required'

    name = forms.CharField(required=True, label=_('* Organization name'))
    sector = forms.CharField(widget=(
        forms.Select(attrs={'class': 'width-200px'}, choices=(('PublicHealth', _('Public Health')), ('Other', _('Other'))))),
                             label=_('Organization Sector'))
    address = forms.CharField(required=True, max_length=30, label=_('* Address'))
    city = forms.CharField(max_length=30, required=True, label=_('* City'))
    state = forms.CharField(max_length=30, required=False, label=_('State / Province'))
    country = forms.CharField(max_length=30, required=True, label=_('* Country'))
    zipcode = forms.CharField(max_length=30, required=True, label=_('* Postal / Zip Code'))
    office_phone = forms.RegexField(required=False, regex="^[^a-zA-Z]*[0-9]+$", max_length=15,
                                    label=_("Office Phone Number"),
                                    error_message=_("Please enter a valid phone number"))
    website = forms.URLField(required=False, label=_('Website Url'))

    class Meta:
        model = Organization


    def update(self):
        if self.is_valid():
            self.save()

        return self


class UserProfileForm(forms.Form):
    required_css_class = 'required'

    title = forms.CharField(max_length=30, required=False)
    first_name = forms.CharField(max_length=30, required=True, label=_('* First name'))
    last_name = forms.CharField(max_length=30, required=True, label=_('* Last name'))
    username = forms.EmailField(max_length=30, required=True, label=_("* Email"), error_messages={
        'invalid': _('Enter a valid email address. Example:name@organization.com')})
    office_phone = forms.RegexField(required=False, regex="^[^a-zA-Z]*[0-9]+$", max_length=15, label=_("Office Phone"),
                                    error_message=_("Please enter a valid phone number"))
    mobile_phone = forms.RegexField(required=False, regex="^[^a-zA-Z]*[0-9]+$", max_length=15, label=_("Mobile Phone"),
                                    error_message=_("Please enter a valid phone number"))
    skype = forms.CharField(max_length=30, required=False, label="Skype")


    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).count() > 0:
            raise ValidationError(_("This email address is already in use. Please supply a different email address"))
        return self.cleaned_data.get('username')


class EditUserProfileForm(UserProfileForm):
    def clean_username(self):
        return self.cleaned_data.get('username')


class RegistrationForm(RegistrationFormUniqueEmail):
    required_css_class = 'required'

    title = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(widget=forms.TextInput(attrs=dict({'class': 'required'},
                                                                                    maxlength=75)),
                             label=_("* Email address"),
                             error_messages={'invalid': _('Enter a valid email address. Example:name@organization.com')})
    first_name = forms.CharField(max_length=30, required=True, label='* First name')
    last_name = forms.CharField(max_length=30, required=True, label='* Last name')
    office_phone = forms.RegexField(required=False, regex="^[^a-zA-Z]*[0-9]+$", max_length=15, label=_("Office Phone"),
                                    error_message=_("Please enter a valid phone number"))
    mobile_phone = forms.RegexField(required=False, regex="^[^a-zA-Z]*[0-9]+$", max_length=15, label=_("Mobile Phone"),
                                    error_message=_("Please enter a valid phone number"))
    skype = forms.CharField(max_length=30, required=False, label="Skype")

    organization_name = forms.CharField(required=True, max_length=30, label=_('* Organization Name'))
    organization_sector = forms.CharField(widget=(
        forms.Select(attrs={'class': 'width-200px'}, choices=(('PublicHealth', 'Public Health'), ('Other', 'Other')))),
                                          label=_('Organization Sector'))
    organization_address = forms.CharField(required=True, max_length=30, label=_('* Address'))
    organization_city = forms.CharField(max_length=30, required=True, label=_('* City'))
    organization_state = forms.CharField(max_length=30, required=False, label=_('State / Province'))
    organization_country = forms.CharField(max_length=30, required=True, label=_('* Country'))
    organization_zipcode = forms.RegexField(required=True, max_length=30, regex="^[a-zA-Z\d-]*$",
                                            error_message=_("Please enter a valid Postal / Zip code"),
                                            label=_('* Postal / Zip Code'))
    organization_office_phone = forms.RegexField(required=False, regex="^[^a-zA-Z]*[0-9]+$", max_length=15,
                                                 label=_("Office Phone Number"),
                                                 error_message=_("Please enter a valid phone number"))
    organization_website = forms.URLField(required=False, label=_('Website Url'))
    username = forms.CharField(max_length=30, required=False)

    def clean(self):
        self.convert_email_to_lowercase()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                msg = _("The two password fields didn't match.")
                self._errors['password1'] = self.error_class([msg])
        return self.cleaned_data

    def convert_email_to_lowercase(self):
        email = self.cleaned_data.get('email')
        if email is not None:
            self.cleaned_data['email'] = email.lower()


class LoginForm(AuthenticationForm):
    required_css_class = 'required'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        self.cleaned_data['username'] = username.lower()
        return self.cleaned_data['username']

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
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive."))


class ResetPasswordForm(PasswordResetForm):
    required_css_class = 'required'


class PasswordSetForm(SetPasswordForm):
    required_css_class = 'required'

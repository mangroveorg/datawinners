import re

from django import forms
from django.contrib.auth.models import User
from datawinners.accountmanagement.helper import is_mobile_number_unique_for_trial_account
from django.forms import HiddenInput, BooleanField
from django.forms.fields import RegexField, CharField, FileField, MultipleChoiceField, EmailField
from django.forms.widgets import CheckboxSelectMultiple, TextInput
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.forms.forms import Form

from datawinners.accountmanagement.models import Organization
from datawinners.entity.datasender_search import datasender_count_with
from mangrove.form_model.form_model import MOBILE_NUMBER_FIELD_CODE, GEO_CODE, GEO_CODE_FIELD_NAME
from mangrove.utils.types import is_empty
from datawinners.entity.fields import PhoneNumberField


class EntityTypeForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    entity_type_regex = CharField(max_length=20, required=False, label=_("New Subject(eg clinic, waterpoint etc)"))

    def clean_entity_type_regex(self):
        value = self.cleaned_data['entity_type_regex']
        if value == '':
            self._errors['entity_type_regex'] = _("You can't leave this empty.")
        elif not re.match("^\s*([A-Za-z\d]+(\s[A-Za-z\d]+)*)\s*$", value):
            self._errors['entity_type_regex'] = _("Please use only letters (a-z), numbers, and spaces.")
        return value


class SubjectForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'

    type = CharField(max_length=30, required=True, label=_("Type"))
    name = CharField(max_length=30, required=True, label=_("Name"))
    uniqueID = CharField(max_length=100, required=True, label=_("Unique Identification Number (ID)"))
    location = CharField(max_length=30, required=True, label=_("Location"))
    description = CharField(max_length=30, required=False, label=_("Description"))
    mobileNumber = CharField(max_length=30, required=False, label=_("Mobile Number"))


def smartphone_icon():
    return ' + <img src="/media/images/smart_phone.png" /><span>Smartphone</span>'


class ReporterRegistrationForm(Form):
    required_css_class = 'required'

    name = RegexField(regex="[^0-9.,\s@#$%&*~]*", max_length=80,
                      error_message=_("Please enter a valid value containing only letters a-z or A-Z or symbols '`- "),
                      label=_("Name"), required=False)
    telephone_number = PhoneNumberField(required=True, label=_("Mobile Number"),
                                        error_message=_("Please enter a valid phone number."))
    geo_code = CharField(max_length=30, required=False, label=_("GPS Coordinates"))

    location = CharField(max_length=500, required=False, label=_("Name"))
    project_id = CharField(required=False, widget=HiddenInput())

    DEVICE_CHOICES = (('sms', mark_safe('<img src="/media/images/mini_mobile.png" /> <span>SMS</span>')), (
        'web', mark_safe('<img src="/media/images/mini_computer.png" /> <span>Web</span>' + smartphone_icon())))
    devices = MultipleChoiceField(label=_('Device'), widget=CheckboxSelectMultiple(), choices=DEVICE_CHOICES,
                                  initial=['sms'], required=False, )
    email = EmailField(required=False, widget=TextInput(attrs=dict({'class': 'required'},
                                                                   maxlength=75)),
                       label=_("E-Mail"),
                       error_messages={
                           'invalid': _('Enter a valid email address. Example:name@organization.com')})

    short_code = CharField(required=False, max_length=12, label=_("ID"),
                           widget=TextInput(attrs=dict({'class': 'subject_field'})))
    generated_id = BooleanField(required=False, initial=True)

    # Needed for telephone number validation
    org_id = None

    def __init__(self, org_id=None, *args, **kwargs):
        self.org_id = org_id
        super(ReporterRegistrationForm, self).__init__(*args, **kwargs)

    def _is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False


    def _geo_code_format_validations(self, lat_long, msg):
        if len(lat_long) != 2:
            self._errors['geo_code'] = self.error_class([msg])
        else:
            try:
                if not (-90 < float(lat_long[0]) < 90 and -180 < float(lat_long[1]) < 180):
                    self._errors['geo_code'] = self.error_class([msg])
            except Exception:
                self._errors['geo_code'] = self.error_class([msg])

    def _geo_code_validations(self):
        geo_code = self.cleaned_data.get("geo_code").strip()

        if not bool(geo_code):
            return

        msg = _(
            "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315")

        geo_code_string = geo_code.strip()
        geo_code_string = geo_code_string.replace(",", " ")
        geo_code_string = re.sub(' +', ' ', geo_code_string)
        if not is_empty(geo_code_string):
            lat_long = geo_code_string.split(" ")
            self._geo_code_format_validations(lat_long, msg)
            self.cleaned_data['geo_code'] = geo_code_string

    def clean(self):
        self.convert_email_to_lowercase()
        if not self.cleaned_data.get('generated_id') and not self.cleaned_data.get('short_code'):
            msg = _('This field is required.')
            self.errors['short_code'] = self.error_class([msg])

        self._geo_code_validations()
        if not self.cleaned_data.get('project_id'):
            self.cleaned_data['is_data_sender'] = False
        else:
            self.cleaned_data['is_data_sender'] = 'True'

        return self.cleaned_data

    def clean_short_code(self):
        short_code = self.cleaned_data.get('short_code')

        if short_code:
            if len(short_code) > 12:
                msg = _("Unique ID should be less than 12 characters")
                self.errors['short_code'] = self.error_class([msg])

            if not re.match("^[a-zA-Z0-9]+$", short_code):
                msg = _("Only letters and numbers are valid")
                self.errors['short_code'] = self.error_class([msg])

        return short_code

    def clean_telephone_number(self):
        """
        Validate telephone number. This expects the dbm to be set on the form before trying to clean.
        """

        organization = Organization.objects.get(org_id=self.org_id)
        mobile_number = self.cleaned_data.get('telephone_number')
        if organization.in_trial_mode:
            if not is_mobile_number_unique_for_trial_account(organization, mobile_number):
                self._errors['telephone_number'] = self.error_class(
                    [_(u"Sorry, this number has already been used for a different DataWinners Basic account.")])
        return mobile_number


    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        email = self.cleaned_data.get('email')
        if not email:
            return email
        mail_filter = User.objects.filter(email=email)
        if datasender_count_with(email) > 0 or mail_filter.exists():
            raise forms.ValidationError(
                _("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']

    def convert_email_to_lowercase(self):
        email = self.cleaned_data.get('email')
        if email is not None:
            self.cleaned_data['email'] = email.lower()

    def requires_web_access(self):
        return self.cleaned_data.get('email')

    def update_errors(self, validation_errors):
        mapper = {MOBILE_NUMBER_FIELD_CODE: 'telephone_number',
                  GEO_CODE: GEO_CODE_FIELD_NAME}
        for field_code, error in validation_errors.iteritems():
            self._errors[mapper.get(field_code)] = self.error_class([_(error)])


class EditReporterRegistrationForm(ReporterRegistrationForm):
    def __init__(self, org_id=None, existing_email=None, *args, **kwargs):
        super(EditReporterRegistrationForm, self).__init__(org_id, *args, **kwargs)
        self.existing_email = existing_email

    def clean(self):
        self.convert_email_to_lowercase()
        self._geo_code_validations()
        return self.cleaned_data

    def clean_email(self):
        new_email = self.cleaned_data.get('email')
        if new_email != self.existing_email:
            return super(EditReporterRegistrationForm, self).clean_email()

        return self.existing_email


class SubjectUploadForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'
    file = FileField(label='Import Subjects')

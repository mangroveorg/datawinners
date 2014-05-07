import re

from django import forms
from django.contrib.auth.models import User
from django.forms import HiddenInput
from django.forms.fields import RegexField, CharField, FileField, MultipleChoiceField, EmailField
from django.forms.widgets import CheckboxSelectMultiple, TextInput
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, ugettext
from django.forms.forms import Form

from datawinners.accountmanagement.models import Organization, DataSenderOnTrialAccount
from mangrove.form_model.form_model import MOBILE_NUMBER_FIELD_CODE
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
        label=_("Name"))
    telephone_number = PhoneNumberField(required=True, label=_("Mobile Number"))
    geo_code = CharField(max_length=30, required=False, label=_("GPS Coordinates"))

    location = CharField(max_length=100, required=False, label=_("Name"))
    project_id = CharField(required=False, widget=HiddenInput())

    DEVICE_CHOICES = (('sms', mark_safe('<img src="/media/images/mini_mobile.png" /> <span>SMS</span>')), ('web', mark_safe('<img src="/media/images/mini_computer.png" /> <span>Web</span>' + smartphone_icon())))
    devices = MultipleChoiceField(label=_('Device'), widget=CheckboxSelectMultiple(), choices=DEVICE_CHOICES,
        initial=['sms'], required=False,)
    email = EmailField(required=False, widget=TextInput(attrs=dict({'class': 'required'},
        maxlength=75)),
        label=_("Email address"),
        error_messages={
            'invalid': _('Enter a valid email address. Example:name@organization.com')})

    short_code = CharField(required=False, max_length=12, label=_("Unique ID"), widget=TextInput(attrs=dict({'class': 'subject_field','disabled':'disabled'})))

#    Needed for telephone number validation
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

    def _geo_code_validations(self, b):
        msg = ugettext(
            "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315")
        geo_code_string = b.strip()
        geo_code_string = (' ').join(geo_code_string.split())
        if not is_empty(geo_code_string):
            lat_long = filter(None, re.split("[ ,]", geo_code_string))
            self._geo_code_format_validations(lat_long, msg)
            self.cleaned_data['geo_code'] = geo_code_string

    def clean(self):
        self.convert_email_to_lowercase()
        location = self.cleaned_data.get("location").strip()
        geo_code = self.cleaned_data.get("geo_code").strip()
        if not (bool(location) or bool(geo_code)):
            msg = _("Please fill out at least one location field correctly.")
            self._errors['location'] = self.error_class([msg])
            self._errors['geo_code'] = self.error_class([msg])
        if bool(geo_code):
            self._geo_code_validations(geo_code)
        return self.cleaned_data

    def clean_short_code(self):
        short_code = self.cleaned_data.get('short_code')

        if short_code:
            self.fields.get("short_code").widget.attrs.pop("disabled")
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
        if organization.in_trial_mode:
            if DataSenderOnTrialAccount.objects.filter(mobile_number=(self.cleaned_data.get('telephone_number'))).exclude(organization=organization).exists():
                self._errors['telephone_number'] = self.error_class(
                    [(u"Sorry, this number has already been used for a different DataWinners trial account.")])
        return self.cleaned_data.get('telephone_number')


    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if not self.requires_web_access():
            return None

        email = self.cleaned_data.get('email')
        if is_empty(email):
            msg = _('This field is required.')
            self._errors['email'] = self.error_class([msg])
            return None

        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']

    def convert_email_to_lowercase(self):
        email = self.cleaned_data.get('email')
        if email is not None:
            self.cleaned_data['email'] = email.lower()

    def requires_web_access(self):
        devices = self.cleaned_data.get('devices')
        return devices.__contains__('web')

    def update_errors(self, validation_errors):
        mapper = {MOBILE_NUMBER_FIELD_CODE: 'telephone_number'}
        error = _(u'Sorry, the telephone number %s has already been registered.') % self.cleaned_data.get('telephone_number')
        self._errors[mapper[MOBILE_NUMBER_FIELD_CODE]]= self.error_class([error])



class SubjectUploadForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'
    file = FileField(label='Import Subjects')

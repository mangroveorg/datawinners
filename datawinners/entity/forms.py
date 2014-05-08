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


class SubjectUploadForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'
    file = FileField(label='Import Subjects')

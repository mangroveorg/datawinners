from django.forms import HiddenInput
from django.forms.fields import RegexField, CharField, FileField
from django.utils.translation import ugettext as _
from django.forms.forms import Form
from mangrove.utils.types import is_empty
from datawinners.entity.fields import PhoneNumberField
class EntityTypeForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    entity_type_regex = RegexField(regex="^[A-Za-z\d\s]+$", max_length=20,
                                   error_message=_("Only letters and numbers are valid"), required=True,
                                   label=_("New Subject(eg clinic, waterpoint etc)"))

class SubjectForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'

    type = CharField(max_length=30, required=True, label=_("Type"))
    name = CharField(max_length=30, required=True, label=_("Name"))
    uniqueID = CharField(max_length=100, required=True, label=_("Unique Identification Number(ID)"))
    location = CharField(max_length=30, required=True, label=_("Location"))
    description = CharField(max_length=30, required=False, label=_("Description"))
    mobileNumber = CharField(max_length=30, required=False, label=_("Mobile Number"))

class ReporterRegistrationForm(Form):
    required_css_class = 'required'

    first_name = RegexField(regex="[^0-9.,\s@#$%&*~]*", max_length=20,
                            error_message=_("Please enter a valid value containing only letters a-z or A-Z or symbols '`- "),
                            label=_("Name"))
    telephone_number = PhoneNumberField(required=True, label=_("Mobile Number"))
    geo_code = CharField(max_length=30, required=False, label=_("GPS: Enter Lat Long"))
    location = CharField(max_length=100, required=False, label=_("Enter location"))
    project_id = CharField(required=False, widget=HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ReporterRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['watermark'] = _("Enter Data Sender's name")
        self.fields['telephone_number'].widget.attrs['watermark'] = _("Enter Data Sender's number eg: ")
        self.fields['location'].widget.attrs['watermark'] = _("Enter region, district or commune")
        self.fields['geo_code'].widget.attrs['watermark'] = _("Enter lat and long eg: 19.3 42.37")

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
        msg = _("Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315")
        geo_code_string = b.strip()
        geo_code_string = (' ').join(geo_code_string.split())
        if not is_empty(geo_code_string):
            lat_long = geo_code_string.split(' ')
            self._geo_code_format_validations(lat_long, msg)
            self.cleaned_data['geo_code'] = geo_code_string

    def clean(self):
        a = self.cleaned_data.get("location")
        b = self.cleaned_data.get("geo_code")
        if not (bool(a) or bool(b)):
            msg = _("Please fill out at least one location field correctly.")
            self._errors['location'] = self.error_class([msg])
            self._errors['geo_code'] = self.error_class([msg])
        if bool(b):
            self._geo_code_validations(b)
        return self.cleaned_data


class SubjectUploadForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'
    file = FileField(label='Import Subjects')

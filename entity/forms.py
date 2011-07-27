from django.core.exceptions import ValidationError
from django.forms.fields import RegexField, CharField, FileField
from django.forms.forms import Form
from mangrove.utils.types import is_empty

class EntityTypeForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    entity_type_regex = RegexField(regex="^[A-Za-z\d\s]+$", max_length=20, error_message="Only letters and numbers are valid", required=True, label="New Subject(eg clinic, waterpoint etc)")

class ReporterRegistrationForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    first_name = RegexField(regex="[^0-9.,\s@#$%&*~]*", max_length=20,
                            error_message="Please enter a valid value containing only letters a-z or A-Z or symbols '`- "
                            ,
                            label="* Name")
    telephone_number = RegexField(required=True, regex="^[^a-zA-Z]*[0-9]+$", max_length=15, label="* Mobile Number",
                                  error_message="Please enter a valid phone number")
    geo_code = CharField(max_length=30, required=False, label="GPS: Enter Lat Long")
    location = CharField(max_length=100, required=False, label="Enter location")

    def __init__(self, *args, **kwargs):
        super(ReporterRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['watermark'] = "Enter Data Sender's name"
        self.fields['telephone_number'].widget.attrs['watermark'] = "Enter Data Sender's number eg: "
        self.fields['location'].widget.attrs['watermark'] = "Enter region, district or commune"
        self.fields['geo_code'].widget.attrs['watermark'] = "Enter lat and long eg: 19.3 42.37"

    def _is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def clean_telephone_number(self):
        return ("").join([each for each in self.cleaned_data['telephone_number'] if self._is_int(each) ])
    
    def clean(self):
        a = self.cleaned_data.get("location")
        b = self.cleaned_data.get("geo_code")
        if not (bool(a) or bool(b)):
            raise ValidationError("Required information for registration. Please fill out at least one location field correctly.")
        return self.cleaned_data


class SubjectUploadForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'
    file = FileField(label='Import Subjects')

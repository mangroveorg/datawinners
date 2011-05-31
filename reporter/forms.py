from django.core.exceptions import ValidationError
from django.forms.fields import CharField, RegexField
from django.forms.forms import Form
from mangrove.utils.types import is_empty


class ReporterRegistrationForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    first_name = RegexField(regex="[^0-9.,\s@#$%&*~]*", max_length=30,
                            error_message="Please enter a valid value containing only letters a-z or A-Z or symbols '`- ",
                             required=True, label="* First Name")
    last_name = RegexField(regex="[^0-9.,\s@#$%&*~]*", max_length=30,
                           error_message="Please enter a valid value containing only letters a-z or A-Z or symbols '`- ",
                            required=True, label="* Last Name")
    telephone_number = CharField(required=True, label="* Telephone Number")
    commune = CharField(max_length=30, required=True, label="* Commune")
    geo_code = CharField(max_length=30, required=False, label="Geo Code")


    def clean_geo_code(self):
        geo_code_string = self.cleaned_data['geo_code']
        if is_empty(geo_code_string):
            return geo_code_string
        lat_long_string = geo_code_string.split(' ')
        if len(lat_long_string) < 2:
            raise ValidationError("GPS coordinates must be in the format 'lat long'.")
        return geo_code_string

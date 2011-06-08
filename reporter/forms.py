# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.core.exceptions import ValidationError
from django.forms.fields import CharField, RegexField
from django.forms.forms import Form
from mangrove.utils.types import is_empty


class ReporterRegistrationForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    first_name = RegexField(regex="[^0-9.,\s@#$%&*~]*", max_length=20,
                            error_message="Please enter a valid value containing only letters a-z or A-Z or symbols '`- ",
                              label="* Name")
    telephone_number = RegexField(required=True, regex="^\d+(-\d+)*$", max_length=15, label="* Mobile Number", error_message="Please enter a valid phone number")
    commune = CharField(max_length=30, required=False, label="Location")
    geo_code = CharField(max_length=30, required=False, label="GPS: Enter Lat Long")


    def clean_geo_code(self):
        geo_code_string = self.cleaned_data['geo_code']
        geo_code_string = geo_code_string.strip()
        if is_empty(geo_code_string):
            return geo_code_string
        lat_long = geo_code_string.split(' ')
        if len(lat_long) != 2:
            raise ValidationError("GPS coordinates must be in the format 'lat long'.")
        if not (-90 < float(lat_long[0]) < 90 and -180 < float(lat_long[1]) < 180):
            raise ValidationError("Incorrect GPS coordinates. Please resubmit.")
        return geo_code_string

    def clean(self):
        a = self.cleaned_data.get("commune")
        b = self.cleaned_data.get("geo_code")
        if not (bool(a) or bool(b)):
            raise ValidationError("Required information for registration. Please fill out at least one location field correctly.")
        return self.cleaned_data

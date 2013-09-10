import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from mangrove.form_model.field import GeoCodeField
from mangrove.form_model.form_model import LOCATION_TYPE_FIELD_NAME
from mangrove.utils.types import is_empty
from mangrove.form_model.validation import GeoCodeConstraint


def get_location_field_code(form_model):
    location_fields = filter(lambda field: field.name == LOCATION_TYPE_FIELD_NAME, form_model.fields)
    return location_fields[0].code if not is_empty(location_fields) else None

def get_geo_code_field_question_code(form_model):
    geo_code_fields = filter(lambda field: field.type == GeoCodeField.type, form_model.fields)
    return geo_code_fields[0].code if not is_empty(geo_code_fields) else None

def get_report_period_question_name_and_datetime_format(form_model):
    field = form_model.event_time_question
    return None if field is None else field.code.lower(), field.date_format

def get_geo_code_fields_question_code(form_model):
    return [field.code for field in form_model.fields if field.type == GeoCodeField.type]

def make_clean_geocode_method(geo_code_field_code):
    def clean_geocode(self):
        lat_long_string = self.cleaned_data[geo_code_field_code]
        lat_long = lat_long_string.replace(",", " ")
        lat_long = re.sub(' +', ' ', lat_long).split(" ")
        try:
            if len(lat_long) != 2:
                raise Exception
            GeoCodeConstraint().validate(latitude=lat_long[0], longitude=lat_long[1])
        except Exception:
            raise ValidationError(_(
                "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"))
        return self.cleaned_data[geo_code_field_code]
    return clean_geocode
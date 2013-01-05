from mangrove.form_model.field import GeoCodeField
from mangrove.form_model.form_model import LOCATION_TYPE_FIELD_NAME, GEO_CODE_FIELD_NAME, FormModel
from mangrove.utils.types import is_empty

def get_location_field_code(form_model):
    location_fields = filter(lambda field: field.name == LOCATION_TYPE_FIELD_NAME, form_model.fields)
    return location_fields[0].code if not is_empty(location_fields) else None

def get_geo_code_field_question_code(form_model):
    geo_code_fields = filter(lambda field: field.type == GeoCodeField.type, form_model.fields)
    return geo_code_fields[0].code if not is_empty(geo_code_fields) else None

def get_report_period_question_name_and_datetime_format(form_model):
    field = form_model.event_time_question
    return None if field is None else field.code.lower(), field.date_format


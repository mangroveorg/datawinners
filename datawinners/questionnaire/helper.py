from mangrove.form_model.form_model import LOCATION_TYPE_FIELD_NAME
from mangrove.utils.types import is_empty

def get_location_field_code(form_model):
    location_fields = filter(lambda field: field.name == LOCATION_TYPE_FIELD_NAME, form_model.fields)
    return location_fields[0].code if not is_empty(location_fields) else None

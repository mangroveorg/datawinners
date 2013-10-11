from collections import OrderedDict
from datawinners.entity.helper import get_entity_type_fields, tabulate_data
from mangrove.datastore.entity import Entity
from mangrove.form_model.field import DateField


def _add_date_field_mapping(mapping_fields, field):
    mapping_fields.update(
        {field.name: {"type": "multi_field", "fields": {
            field.name: {"type": "string"},
            field.name + "_value": {"type": "date", "format": DateField.FORMAT_DATE_DICTIONARY.get(field.date_format),
                                    "ignore_malformed": True}
        }}})


def _add_text_field_mapping(mapping_fields, field):
    mapping_fields.update(
        {field.name: {"type": "multi_field", "fields": {
            field.name: {"type": "string"},
            field.name + "_value": {"type": "string", "index_analyzer": "sort_analyzer",
                                    "include_in_all": False}
        }}})


def _mapping(key, fields):
    mapping_fields = {}
    mapping = {"date_detection": False, "properties": mapping_fields}
    for field in fields:
        if isinstance(field, DateField):
            _add_date_field_mapping(mapping_fields, field)
        else:
            _add_text_field_mapping(mapping_fields, field)
    return {key: mapping}


def _entity_dict(entity_type, entity_doc, dbm, form_model):
    entity = Entity.get(dbm, entity_doc.id)
    fields, labels, codes = get_entity_type_fields(dbm, type=entity_type)
    data = tabulate_data(entity, form_model, codes)
    dictionary = OrderedDict()
    for index in range(0, len(fields)):
        dictionary.update({fields[index]: data['cols'][index]})
    dictionary.update({"entity_type": entity_type})
    dictionary.update({"void": entity.is_void()})
    return dictionary
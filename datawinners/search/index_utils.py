from collections import OrderedDict
import elasticutils
from datawinners.entity.helper import get_entity_type_fields, tabulate_data
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.datastore.entity import Entity
from mangrove.form_model.field import DateField
from mangrove.form_model.form_model import get_form_model_by_entity_type


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
            field.name + "_value": {"type": "string", "index": "not_analyzed", "include_in_all": False}
        }}})


def _mapping(form_model):
    mapping_fields = {}
    mapping = {"date_detection": False, "properties": mapping_fields}
    for field in form_model.fields:
        if isinstance(field, DateField):
            _add_date_field_mapping(mapping_fields, field)
        else:
            _add_text_field_mapping(mapping_fields, field)
    return {form_model.form_code: mapping}


def _update_mapping(dbm, form_model):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    es.put_mapping(dbm.database_name, form_model.entity_type[0], _mapping(form_model))


def _entity_dict(entity_type, entity_doc, dbm):
    entity = Entity.get(dbm, entity_doc.id)
    fields, labels, codes = get_entity_type_fields(dbm, type=entity_type)
    form_model = get_form_model_by_entity_type(dbm, [entity_type])
    data = tabulate_data(entity, form_model, codes)
    dictionary = OrderedDict()
    for index in range(0, len(fields)):
        dictionary.update({fields[index]: data['cols'][index]})
    dictionary.update({"entity_type": entity_type})
    dictionary.update({"void": entity.is_void()})
    return dictionary
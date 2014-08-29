from collections import OrderedDict
from string import lower
import elasticutils
from datawinners.entity.helper import get_entity_type_fields, tabulate_data
from datawinners.search.submission_index_meta_fields import submission_meta_field_names
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT
from mangrove.datastore.entity import Entity
from mangrove.form_model.field import DateField


def _add_date_field_mapping(mapping_fields, field_def):
    name = field_def["name"]
    mapping_fields.update(
        {name: {"type": "multi_field", "fields": {
            name: {"type": "string"},
            name + "_value": {"type": "date", "format": DateField.FORMAT_DATE_DICTIONARY.get(field_def["date_format"]),
                              "ignore_malformed": True}
        }}})


def _add_text_field_mapping(mapping_fields, field_def):
    name = field_def["name"]
    mapping_fields.update(
        {name: {"type": "multi_field", "fields": {
            name: {"type": "string"},
            name + "_value": {"type": "string", "index_analyzer": "sort_analyzer", "include_in_all": False}
        }}})




def get_field_definition(form_field, field_name=None):
    field_def = {"name": field_name or lower(form_field.name)}
    if isinstance(form_field, DateField):
        field_def.update({"type": "date"})
        field_def.update({"date_format": form_field.date_format})
    else:
        field_def.update({"type": 'string'})
    return field_def


def get_fields_mapping(doc_type, fields):
    fields_definition = [get_field_definition(field) for field in fields]
    return get_fields_mapping_by_field_def(doc_type, fields_definition)


def get_fields_mapping_by_field_def(doc_type, fields_definition):
    """
    fields_definition   = [{"name":form_model_id_q1, "type":"date", "date_format":"MM-yyyy"},{"name":form_model_id_q1, "type":"string"}]
    """
    mapping_fields = {}
    mapping = {"date_detection": False, "properties": mapping_fields}
    for field_def in fields_definition:
        if field_def.get("type") is "date":
            _add_date_field_mapping(mapping_fields, field_def)
        else:
            _add_text_field_mapping(mapping_fields, field_def)
    return {doc_type: mapping}


def _entity_dict(entity_type, entity_doc, dbm, form_model):
    entity = Entity.get(dbm, entity_doc.id)
    fields, labels, codes = get_entity_type_fields(dbm, form_model.form_code)
    data = tabulate_data(entity, form_model, codes)
    dictionary = OrderedDict()
    for index in range(0, len(fields)):
        dictionary.update({fields[index]: data['cols'][index]})
    dictionary.update({"entity_type": entity_type})
    dictionary.update({"void": entity.is_void()})
    return dictionary


def subject_dict(entity_type, entity_doc, dbm, form_model):
    entity = Entity.get(dbm, entity_doc.id)
    field_names, labels, codes = get_entity_type_fields(dbm, form_model.form_code)
    data = tabulate_data(entity, form_model, codes)
    dictionary = OrderedDict()
    for index in range(0, len(field_names)):
        dictionary.update({es_questionnaire_field_name(codes[index],form_model.id): data['cols'][index]})
    dictionary.update({"entity_type": entity_type})
    dictionary.update({"void": entity.is_void()})
    return dictionary


def get_elasticsearch_handle(timeout=ELASTIC_SEARCH_TIMEOUT):
    return elasticutils.get_es(urls=ELASTIC_SEARCH_URL, timeout=timeout)


# def es_field_name(field_code, form_model_id):
#     """
#         prefixes form_model id to namespace all additional fields on questionnaire (ds_name, ds_id, status and date are not prefixed)
#     :param field_code:
#     """
#     if is_submission_meta_field(field_code):
#         return es_submission_meta_field_name(field_code)
#     else:
#         return es_questionnaire_field_name(field_code, form_model_id)

def es_submission_meta_field_name(field_code):
    """
        returns the field name for meta fields in the submission document
    :param field_code:
    """
    return field_code


def es_questionnaire_field_name(field_code, form_model_id, parent_field_code=None):
    """
        prefixes form_model id to namespace all fields on questionnaire
    """
    code = "%s-%s" % (parent_field_code, field_code) if parent_field_code else field_code
    return "%s_%s" % (form_model_id, code)

def es_unique_id_code_field_name(es_field_name):
    return es_field_name+'_unique_code'

def is_submission_meta_field(field_name):
    return submission_meta_field_names.has_key(field_name)

def delete_mapping(db_name, doc_type):
    es = get_elasticsearch_handle()
    es.delete_all(db_name, doc_type)

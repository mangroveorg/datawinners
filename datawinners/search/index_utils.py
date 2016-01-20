from collections import OrderedDict
from string import lower
import elasticutils
from datawinners.search.submission_index_meta_fields import submission_meta_field_names
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT
from mangrove.datastore.entity import Entity, Contact
from mangrove.form_model.field import DateField, TimeField, DateTimeField, field_attributes,\
    UniqueIdField
from mangrove.form_model.project import get_entity_type_fields, tabulate_data, \
    get_field_value, get_field_default_value
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE
from mangrove.datastore.cache_manager import get_cache_manager
from __builtin__ import isinstance
from mangrove.datastore.queries import get_all_by_type
from datawinners.entity.import_data import get_entity_type_info
from mangrove.datastore.entity import get_by_short_code_include_voided, Entity, Contact
from mangrove.errors.MangroveException import DataObjectNotFound



def _add_date_field_mapping(mapping_fields, field_def):
    name = field_def["name"]
    mapping_fields.update(
        {name: {"type": "multi_field", "fields": {
            name: {"type": "date", "format": DateField.FORMAT_DATE_DICTIONARY.get(field_def["date_format"]),
                   "ignore_malformed": True},
            name + "_value": {"type": "date", "format": DateField.FORMAT_DATE_DICTIONARY.get(field_def["date_format"]),
                              "ignore_malformed": True}
        }}})


def _add_text_field_mapping(mapping_fields, field_def):
    name = field_def["name"]
    mapping_fields.update(
        {name: {"type": "multi_field", "fields": {
            name: {"type": "string"},
            name + "_value": {"type": "string", "index_analyzer": "sort_analyzer", "include_in_all": False},
            name + "_exact": {"type": "string", "index": "not_analyzed", "include_in_all": False},

        }}})


def get_field_definition(form_field, field_name=None):
    field_def = {"name": field_name or lower(form_field.name)}
    if form_field.type in [field_attributes.DATE_FIELD, field_attributes.TIME, field_attributes.DATE_TIME]:
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


def _contact_dict(entity_doc, dbm, form_model):
    contact = Contact.get(dbm, entity_doc.id)
    fields, labels, codes = get_entity_type_fields(dbm, form_model.form_code)
    data = tabulate_data(contact, form_model, codes)
    dictionary = OrderedDict()
    for index in range(0, len(fields)):
        dictionary.update({fields[index]: data['cols'][index]})
    dictionary.update({"entity_type": REPORTER_ENTITY_TYPE})
    dictionary.update({"void": contact.is_void()})

    return dictionary


def lookup_entity(dbm, key, entity_type):
    try:
        if key:
            data_dict = {}
            entity_type_info = get_entity_type_info(entity_type, dbm)
            names_to_codes_map = {}
            for name, code in zip(entity_type_info['names'], entity_type_info['codes']):
                names_to_codes_map[name] = code
            data = get_by_short_code_include_voided(dbm, key, entity_type).data_value()
            for key, value in data.iteritems():
                if names_to_codes_map.get(key):
                    data_dict[names_to_codes_map[key]] = value['value']
            return data_dict
    except DataObjectNotFound:
        pass
    return {
        'q2': " "
    }


def _subject_data(dbm, entity, form_model):
    source_data = OrderedDict()
    for field in form_model.fields:
        value = get_field_value(field.name, entity)
        field.set_value(value)
        if isinstance(field, UniqueIdField):
            unique_id_name = lookup_entity(dbm, str(value), [field.unique_id_type]).get('q2')
            source_data[es_questionnaire_field_name(field.code + '_unique_code', form_model.id)] = value if value else ''
            source_data[es_questionnaire_field_name(field.code, form_model.id)] = unique_id_name
        elif field.name in entity.data:
            source_data[es_questionnaire_field_name(field.code, form_model.id)] = field.stringify()
        else:
            source_data[es_questionnaire_field_name(field.code, form_model.id)] = field.stringify()

    return source_data

    
def subject_dict(entity_type, entity_doc, dbm, form_model):
    entity = Entity.get(dbm, entity_doc.id)
    source_data = _subject_data(dbm, entity, form_model)
    source_data.update({"entity_type": entity_type})
    source_data.update({"void": entity.is_void()})
    return source_data

def get_elasticsearch_handle(timeout=ELASTIC_SEARCH_TIMEOUT):
    return elasticutils.get_es(urls=ELASTIC_SEARCH_URL, timeout=timeout)


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
    return es_field_name + '_unique_code'


def es_unique_id_details_field_name(es_field_name):
    return es_field_name + '_details'


def is_submission_meta_field(field_name):
    return submission_meta_field_names.has_key(field_name)


def delete_mapping(db_name, doc_type):
    es = get_elasticsearch_handle()
    es.delete_all(db_name, doc_type)


def safe_getattr(result, key, default=None):
    if hasattr(result, key):
        return getattr(result, key)
    return default

def update_reindex_status(db_name, questionnaire_id, **kwargs):
    indexes_out_of_sync = get_cache_manager().get('indexes_out_of_sync')
    filtered_items = [(index, info) for index, info in enumerate(indexes_out_of_sync) 
                   if info['db_name'] == db_name and info['questionnaire_id'] == questionnaire_id]
    if filtered_items:
        i, info = filtered_items[0]
        info.update(**kwargs)
        indexes_out_of_sync[i] = info

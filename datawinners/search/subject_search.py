from collections import OrderedDict
import elasticutils
from datawinners.main.database import get_database_manager
from mangrove.datastore.entity import Entity
from datawinners.entity.import_data import get_entity_type_fields, _tabulate_data
from mangrove.form_model.field import DateField
from mangrove.form_model.form_model import get_form_model_by_entity_type, FormModel, REGISTRATION_FORM_CODE
from datawinners.settings import ELASTIC_SEARCH_URL


def subject_search_update(entity_doc, dbm):
    if entity_doc.aggregation_paths['_type'] == ['reporter']:
        return
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    if entity_doc.data:
        entity_type = entity_doc.aggregation_paths['_type'][0].lower()
        es.index(dbm.database_name, entity_type, entity_dict(entity_type, entity_doc, dbm), id=entity_doc.id)
    es.refresh(dbm.database_name)


def subject_model_change_handler(form_model_doc, dbm):
    form_model = FormModel.new_from_doc(dbm, form_model_doc)
    if form_model.is_entity_registration_form() and form_model.form_code != REGISTRATION_FORM_CODE:
        update_mapping(dbm, form_model)


def add_date_field_mapping(mapping_fields, field):
    mapping_fields.update(
        {field.name: {"type": "multi_field", "fields": {
            field.name: {"type": "string"},
            field.name + "_value": {"type": "date", "format": DateField.FORMAT_DATE_DICTIONARY.get(field.date_format),
                                    "ignore_malformed": True}
        }}})


def add_text_field_mapping(mapping_fields, field):
    mapping_fields.update(
        {field.name: {"type": "multi_field", "fields": {
            field.name: {"type": "string"},
            field.name + "_value": {"type": "string", "index": "not_analyzed", "include_in_all": False}
        }}})


def mapping(form_model):
    mapping_fields = {}
    mapping = {"date_detection": False, "properties": mapping_fields}
    for field in form_model.fields:
        if isinstance(field, DateField):
            add_date_field_mapping(mapping_fields, field)
        else:
            add_text_field_mapping(mapping_fields, field)
    return {form_model.form_code: mapping}


def update_mapping(dbm, form_model):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    es.put_mapping(dbm.database_name, form_model.entity_type[0], mapping(form_model))


def entity_dict(entity_type, entity_doc, dbm):
    entity = Entity.get(dbm, entity_doc.id)
    fields, labels, codes = get_entity_type_fields(dbm, type=entity_type)
    form_model = get_form_model_by_entity_type(dbm, [entity_type])
    data = _tabulate_data(entity, form_model, codes)
    dictionary = OrderedDict()
    for index in range(0, len(fields)):
        dictionary.update({fields[index]: data['cols'][index]})
    dictionary.update({"entity_type": entity_type})
    dictionary.update({"void": entity.is_void()})
    return dictionary


def S(index_name, mapping_name, start_index, number_of_results):
    return elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes(index_name).doctypes(mapping_name)[
           start_index:start_index + number_of_results]

def paginated_search(user, subject_type, search_params):
    start_result_number = search_params.get("start_result_number")
    number_of_results = search_params.get("number_of_results")
    order = search_params.get("order")
    order_by = search_params.get("order_by")
    manager = get_database_manager(user)

    search_text = search_params.get("search_text")

    header_dict = header_fields(manager, subject_type)

    search = S(manager.database_name, subject_type, start_result_number, number_of_results).order_by(
        order + header_dict.keys()[order_by] + "_value").filter(void=False)

    search_text = replace_special_chars(search_text)
    if search_text:
        raw_query = {"query_string": {"fields": header_dict.keys(), "query": search_text}}
        query = search.query_raw(raw_query)
    else:
        query = search.query()
    subjects = []
    for res in query.values_dict(tuple(header_dict.keys())):
        subject = []
        for key in header_dict:
            subject.append(res.get(key))
        subjects.append(subject)
    return query.count(), search.count(), subjects


def search(user, subject_type, search_text):
    manager = get_database_manager(user)
    header_dict = header_fields(manager, subject_type)
    search = elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes(manager.database_name).doctypes(subject_type)
    search_text = replace_special_chars(search_text)

    if search_text:
        raw_query = {"query_string": {"fields": header_dict.keys(), "query": search_text}}
        query = search.query_raw(raw_query)
    else:
        query = search.query()
    subjects = []
    for res in query.values_dict(tuple(header_dict.keys())):
        subject = []
        for key in header_dict:
            subject.append(res.get(key))
        subjects.append(subject)
    return subjects


def header_fields(manager, subject_type):
    header_dict = OrderedDict()
    form_model = get_form_model_by_entity_type(manager, [subject_type])
    for field in form_model.fields:
        header_dict.update({field.name: field.label})
    return header_dict


def replace_special_chars(search_text):
    lucene_special_chars = ['\\', '+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']', '^', '"', '~', '*', '?', ':']
    for char in lucene_special_chars:
        search_text = search_text.replace(char, '\\' + char)
    return search_text

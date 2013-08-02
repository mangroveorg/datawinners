import elasticutils
from datawinners.main.database import get_database_manager
from mangrove.datastore.entity import Entity
from datawinners.entity.import_data import get_entity_type_fields, _tabulate_data
from mangrove.form_model.field import DateField
from mangrove.form_model.form_model import get_form_model_by_entity_type
from datawinners.settings import ELASTIC_SEARCH_URL


def add_date_field_mapping(mapping_fields, field):
    mapping_fields.update(
        {field.name: {"type": "multi_field", "fields": {
            field.name: {"type": "string"},
            field.name + "_value": {"type": "date", "format": DateField.FORMAT_DATE_DICTIONARY.get(field.date_format),
                                    "ignore_malformed": True}
        }}})


def mapping(form_model):
    mapping_fields = {}
    mapping = {"date_detection": False, "properties": mapping_fields}
    for field in form_model.fields:
        if isinstance(field, DateField):
            add_date_field_mapping(mapping_fields, field)
    return {form_model.form_code: mapping}


def update_mapping(dbm, form_model):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    es.put_mapping(dbm.database_name, form_model.form_code, mapping(form_model))


def update_search(entity_doc, dbm):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    if entity_doc.data:
        entity_type = entity_doc.aggregation_paths['_type'][0].lower()
        es.index(dbm.database_name, entity_type, entity_dict(entity_type, entity_doc, dbm), id=entity_doc.id)
    es.refresh(dbm.database_name)


def entity_dict(entity_type, entity_doc, dbm):
    entity = Entity.get(dbm, entity_doc.id)
    fields, labels, codes = get_entity_type_fields(dbm, type=entity_type)
    form_model = get_form_model_by_entity_type(dbm, [entity_type])
    data = _tabulate_data(entity, form_model, codes)
    dictionary = {}
    for index in range(0, len(fields)):
        dictionary.update({fields[index]: data['cols'][index]})
    dictionary.update({"entity_type": entity_type})
    return dictionary


def S(index_name, mapping_name, start_index, number_of_results):
    return elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes(index_name).doctypes(mapping_name)[
           start_index:start_index + number_of_results]


def search(request, subject_type):
    search_text = request.POST.get('sSearch', '').strip()
    start_result_number = int(request.POST.get('iDisplayStart'))
    number_of_results = int(request.POST.get('iDisplayLength'))

    manager = get_database_manager(request.user)
    header_dict = header_fields(manager, subject_type)
    search = S(manager.database_name, subject_type, start_result_number, number_of_results)
    query = search.query()
    if search_text:
        raw_query = {"query_string": {"fields": header_dict.keys(), "query": search_text}}
        query = search.query_raw(raw_query)
    subjects = []
    for res in query.values_dict(tuple(header_dict.keys())):
        subject = []
        for key in header_dict:
            subject.append(res.get(key))
        subjects.append(subject)
    return query.count(), search.count(), subjects


def header_fields(manager, subject_type):
    header_dict = {}
    form_model = get_form_model_by_entity_type(manager, [subject_type])
    for field in form_model.fields:
        header_dict.update({field.name: field.label})
    return header_dict

from collections import OrderedDict
import elasticutils
from datawinners.entity.helper import get_entity_type_fields, tabulate_data
from datawinners.main.database import get_database_manager
from mangrove.datastore.entity import Entity
from mangrove.form_model.field import DateField
from mangrove.form_model.form_model import get_form_model_by_entity_type, FormModel, REGISTRATION_FORM_CODE, header_fields
from datawinners.settings import ELASTIC_SEARCH_URL


def subject_search_update(entity_doc, dbm):
    if entity_doc.aggregation_paths['_type'] == ['reporter']:
        return
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    if entity_doc.data:
        entity_type = entity_doc.aggregation_paths['_type'][0].lower()
        es.index(dbm.database_name, entity_type, _entity_dict(entity_type, entity_doc, dbm), id=entity_doc.id)
    es.refresh(dbm.database_name)


def subject_model_change_handler(form_model_doc, dbm):
    form_model = FormModel.new_from_doc(dbm, form_model_doc)
    if form_model.is_entity_registration_form() and form_model.form_code != REGISTRATION_FORM_CODE:
        _update_mapping(dbm, form_model)


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


class SubjectQuery():
    def __init__(self):
        self.response_creator = SubjectQueryResponseCreator()
        self.elastic_utils_helper = ElasticUtilsHelper()
        self.query_builder = SubjectQueryBuilder()

    def _getDatabaseName(self, user):
        return get_database_manager(user).database_name

    def _subject_headers(self, user, subject_type):
        return header_fields(get_database_manager(user), subject_type).keys()

    def query(self, user, subject_type, query_text):
        subject_headers = self._subject_headers(user, subject_type)
        query = self.query_builder.create_query(subject_type, self._getDatabaseName(user))
        query_all_results = query[:query.count()]
        query_with_criteria = self.query_builder.add_query_criteria(subject_headers, query_text, query_all_results)
        subjects = self.response_creator.create_response(subject_headers, query_with_criteria)
        return subjects

    def paginated_query(self, user, subject_type, query_params):
        subject_headers = self._subject_headers(user, subject_type)
        paginated_query = self.query_builder.create_paginated_query(subject_type, self._getDatabaseName(user), {
            "start_result_number": query_params["start_result_number"],
            "number_of_results": query_params["number_of_results"],
            "order_field": subject_headers[query_params["order_by"]],
            "order": query_params["order"]
        })
        query_with_criteria = self.query_builder.add_query_criteria(subject_headers, query_params["search_text"], paginated_query)
        subjects = self.response_creator.create_response(subject_headers, query_with_criteria)
        return query_with_criteria.count(), paginated_query.count(), subjects


class SubjectQueryBuilder():
    def __init__(self):
        self.elastic_utils_helper = ElasticUtilsHelper()

    def create_query(self, subject_type, database_name):
        return elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes(database_name).doctypes(subject_type) \
            .filter(void=False)

    def create_paginated_query(self, subject_type, database_name, query_params):
        start_result_number = query_params.get("start_result_number")
        number_of_results = query_params.get("number_of_results")
        order = query_params.get("order")
        order_by = query_params.get("order_field")

        return self.create_query(subject_type, database_name).order_by(order + order_by + "_value") \
            [start_result_number:start_result_number + number_of_results]

    def add_query_criteria(self, query_fields, query_text, search):
        if query_text:
            query_text_escaped = self.elastic_utils_helper.replace_special_chars(query_text)
            raw_query = {
                "query_string": {
                    "fields": tuple(query_fields),
                    "query": query_text_escaped
                }
            }
            return search.query_raw(raw_query)

        return search.query()


class ElasticUtilsHelper():
    def replace_special_chars(self, search_text):
        lucene_special_chars = ['\\', '+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']', '^', '"', '~', '*', '?',
                                ':']
        for char in lucene_special_chars:
            search_text = search_text.replace(char, '\\' + char)
        return search_text


class SubjectQueryResponseCreator():
    def create_response(self, required_field_names, query):
        subjects = []
        for res in query.values_dict(tuple(required_field_names)):
            subject = []
            for key in required_field_names:
                subject.append(res.get(key))
            subjects.append(subject)
        return subjects
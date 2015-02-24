import elasticutils

from datawinners.search.index_utils import es_questionnaire_field_name
from mangrove.form_model.form_model import header_fields, get_form_model_by_entity_type
from mangrove.form_model.form_model import REPORTER
from datawinners.main.database import get_database_manager
from datawinners.search.query import Query, QueryBuilder
from mangrove.form_model.project import get_entity_type_fields


class DatasenderQuery(Query):
    def __init__(self, query_params=None):
        Query.__init__(self, DatasenderQueryResponseCreator(), DataSenderQueryBuilder(), query_params)

    def get_headers(self, user, entity_type=None):
        fields, old_labels, codes = get_entity_type_fields(get_database_manager(user))
        fields.append("devices")
        fields.append('projects')
        fields.append('groups')
        return fields

    def query(self, user, query_text):
        subject_headers = self.get_headers(user)
        query = self.query_builder.get_query(database_name=self._getDatabaseName(user), doc_type=REPORTER)
        query_all_results = query[:query.count()]
        query_with_criteria = self.query_builder.add_query_criteria(subject_headers, query_all_results, query_text)
        return self.response_creator.create_response(subject_headers, query_with_criteria)


class MyDataSenderQuery(Query):
    def __init__(self, query_params=None):
        Query.__init__(self, MyDatasenderQueryResponseCreator(), DataSenderQueryBuilder(), query_params)

    def get_headers(self, user, entity_type=None):
        fields, old_labels, codes = get_entity_type_fields(get_database_manager(user))
        fields.append("devices")
        return fields

    def filtered_query(self, user, project_name, query_params):
        entity_headers = self.get_headers(user, REPORTER)
        query = self.query_builder.get_query(database_name=self._getDatabaseName(user), doc_type=REPORTER)
        paginated_query = self.query_builder.create_paginated_query(query, {
            "start_result_number": query_params["start_result_number"],
            "number_of_results": query_params["number_of_results"],
            "sort_field": entity_headers[query_params["order_by"]],
            "order": query_params["order"]
        })
        query_with_criteria = self.query_builder.add_query_criteria(entity_headers, paginated_query, query_params["search_text"],
                                                                    ).filter(projects_value=project_name)

        entities = self.response_creator.create_response(entity_headers, query_with_criteria)
        return query_with_criteria.count(), paginated_query.count(), entities

    def query_by_project_name(self, user, project_name, search_text):
        entity_headers = self.get_headers(user)
        query = self.query_builder.get_query(database_name=self._getDatabaseName(user), doc_type=REPORTER)
        query = query[:query.count()]
        query = self.query_builder.add_query_criteria(entity_headers, query, search_text).filter(
            projects_value=project_name)
        return self.response_creator.create_response(entity_headers, query)


class DataSenderQueryBuilder(QueryBuilder):
    def get_query(self, database_name, doc_type=REPORTER):
        query = QueryBuilder().get_query(database_name=database_name, doc_type=doc_type)
        return query.filter(~ elasticutils.F(short_code_value='test'))


class SubjectQuery(Query):
    def __init__(self, query_params=None):
        Query.__init__(self, SubjectQueryResponseCreator(), QueryBuilder(), query_params)

    def get_headers(self, user, subject_type):
        manager = get_database_manager(user)
        form_model = get_form_model_by_entity_type(manager, [subject_type])
        subject_es_headers = []
        for code in header_fields(form_model, key_attribute='code').keys():
            subject_es_headers.append(es_questionnaire_field_name(code, form_model.id))
        return subject_es_headers

    def query(self, user, subject_type, query_text):
        subject_headers = self.get_headers(user, subject_type)
        query = self.query_builder.get_query(database_name=self._getDatabaseName(user), doc_type=subject_type)
        query_all_results = query[:query.count()]
        query_with_criteria = self.query_builder.add_query_criteria(subject_headers, query_all_results, query_text)
        subjects = self.response_creator.create_response(subject_headers, query_with_criteria)
        return subjects


class SubjectQueryResponseCreator():
    def create_response(self, required_field_names, query):
        subjects = []
        for res in query.values_dict(tuple(required_field_names)):
            subject = []
            for key in required_field_names:
                subject.append(res.get(key))
            subjects.append(subject)
        return subjects


class DatasenderQueryResponseCreator():
    def create_response(self, required_field_names, query):
        datasenders = []
        for res in query.values_dict(tuple(required_field_names)):
            result = []
            for key in required_field_names:
                if key is "devices":
                    self.add_check_symbol_for_row(res, result)
                elif key is "projects":
                    result.append(", ".join(res.get(key)))
                else:
                    result.append(res.get(key))
            datasenders.append(result)
        return datasenders

    def add_check_symbol_for_row(self, datasender, result):
        check_img = '<img alt="Yes" src="/media/images/right_icon.png" class="device_checkmark">'
        if "email" in datasender.keys() and datasender["email"]:
            result.extend([check_img + check_img + check_img])
        else:
            result.extend([check_img])


class MyDatasenderQueryResponseCreator(DatasenderQueryResponseCreator):
    def create_response(self, required_field_names, query):
        datasenders = []
        for res in query.values_dict(tuple(required_field_names)):
            result = []
            for key in required_field_names:
                if key is "devices":
                    self.add_check_symbol_for_row(res, result)
                elif key is "projects":
                    continue
                else:
                    result.append(res.get(key))
            datasenders.append(result)
        return datasenders

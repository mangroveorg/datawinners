import elasticutils
from datawinners.main.database import get_database_manager
from mangrove.form_model.form_model import header_fields
from datawinners.settings import ELASTIC_SEARCH_URL


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
        query_with_criteria = self.query_builder.add_query_criteria(subject_headers, query_params["search_text"],
                                                                    paginated_query)
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
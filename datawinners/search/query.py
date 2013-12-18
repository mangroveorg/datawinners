from string import lower
import elasticutils
from datawinners.main.database import get_database_manager
from datawinners.settings import ELASTIC_SEARCH_URL


class Query(object):
    def __init__(self, response_creator, query_builder, query_params):
        self.elastic_utils_helper = ElasticUtilsHelper()
        self.query_builder = query_builder
        self.response_creator = response_creator
        self.query_params = query_params

    def _getDatabaseName(self, user):
        return get_database_manager(user).database_name

    def get_headers(self, user, entity_type):
        pass

    def populate_query_options(self, entity_headers):
        options = {
            "start_result_number": self.query_params["start_result_number"],
            "number_of_results": self.query_params["number_of_results"],
            "order": self.query_params["order"],
        }

        #if self.query_params["order_by"] > 0:
        options.update({"order_field": entity_headers[self.query_params.get("order_by")]})

        return options

    def query_to_be_paginated(self, entity_type, user):
        entity_headers = self.get_headers(user, entity_type)
        options = self.populate_query_options(entity_headers)
        query = self.query_builder.create_query(self._getDatabaseName(user), entity_type)
        paginated_query = self.query_builder.create_paginated_query(query, options)
        search_text = lower(
            self.query_params.get("search_text") or self.query_params.get("search_filters", {}).get("search_text", ''))
        query_with_criteria = self.query_builder.add_query_criteria(entity_headers, paginated_query, search_text,
                                                                    query_params=self.query_params)
        return entity_headers, paginated_query, query_with_criteria

    def paginated_query(self, user, entity_type):
        entity_headers, paginated_query, query_with_criteria = self.query_to_be_paginated(entity_type, user)
        entities = self.response_creator.create_response(entity_headers, query_with_criteria)
        return query_with_criteria.count(), paginated_query.count(), entities


class QueryBuilder(object):
    def __init__(self):
        self.elastic_utils_helper = ElasticUtilsHelper()

    def create_query(self, database_name, doc_type):
        return elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes(database_name).doctypes(doc_type).filter(void=False)

    def create_paginated_query(self, query, query_params):
        start_result_number = query_params.get("start_result_number")
        number_of_results = query_params.get("number_of_results")
        order = query_params.get("order")
        order_by = query_params.get("order_field")
        #query = self.create_query(doc_type, database_name)
        if order_by:
            query = query.order_by(order + order_by + "_value")
        return query[start_result_number:start_result_number + number_of_results]

    def add_query_criteria(self, query_fields, query, query_text, query_params=None):
        if query_text:
            query_text_escaped = self.elastic_utils_helper.replace_special_chars(query_text)
            raw_query = {
                "query_string": {
                    "fields": tuple(query_fields),
                    "query": query_text_escaped
                }
            }
            return query.query_raw(raw_query)

        return query.query()


class ElasticUtilsHelper():
    def replace_special_chars(self, search_text):
        lucene_special_chars = ['\\', '+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']', '^', '"', '~', '*', '?',
                                '/',
                                ':']
        for char in lucene_special_chars:
            search_text = search_text.replace(char, '\\' + char)
        return search_text



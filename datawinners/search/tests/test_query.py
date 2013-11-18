from unittest import TestCase
from mock import patch, Mock
from datawinners.search.query import QueryBuilder, ElasticUtilsHelper


class TestQueryBuilder(TestCase):
    def test_should_create_query_with_given_search_url(self):
        with patch("datawinners.search.query.elasticutils") as elasticUtilsMock:
            with patch("datawinners.search.query.ELASTIC_SEARCH_URL") as searchUrl:
                elasticUtilsMock.S.return_value = elasticUtilsMock

                QueryBuilder().create_query("subject_type", "database_name")

                elasticUtilsMock.S.assert_called_with()
                elasticUtilsMock.es.assert_called_with(urls=searchUrl)

    def test_should_create_query_with_index_as_given_database_name(self):
        with patch("datawinners.search.query.elasticutils") as elasticUtilsMock:
            elasticUtilsMock.S.return_value = elasticUtilsMock
            elasticUtilsMock.es.return_value = elasticUtilsMock

            QueryBuilder().create_query("entity_type", "database_name")

            elasticUtilsMock.indexes.assert_called_with("database_name")

    def test_should_create_query_with_document_type_as_given_subject_type(self):
        with patch("datawinners.search.query.elasticutils") as elasticUtilsMock:
            elasticUtilsMock.S.return_value = elasticUtilsMock
            elasticUtilsMock.es.return_value = elasticUtilsMock
            elasticUtilsMock.indexes.return_value = elasticUtilsMock

            QueryBuilder().create_query("subject_type", "database_name")

            elasticUtilsMock.doctypes.assert_called_with("subject_type")

    def test_should_filter_query_with_only_non_void_documents(self):
        with patch("datawinners.search.query.elasticutils") as elasticUtilsMock:
            elasticUtilsMock.S.return_value = elasticUtilsMock
            elasticUtilsMock.es.return_value = elasticUtilsMock
            elasticUtilsMock.indexes.return_value = elasticUtilsMock
            elasticUtilsMock.doctypes.return_value = elasticUtilsMock

            QueryBuilder().create_query("subject_type", "database_name")

            elasticUtilsMock.filter.assert_called_with(void=False)

    def test_should_create_ordered_query_with_given_order_parameters(self):
        with patch("datawinners.search.query.elasticutils") as elasticUtilsMock:
            with patch("datawinners.search.query.QueryBuilder.create_query") as query:
                query.return_value = elasticUtilsMock
                query_params = {
                    "start_result_number": 1,
                    "number_of_results": 10,
                    "order": "-",
                    "order_field": "field_name_to_order_by"
                }

                query_builder = QueryBuilder()
                query_builder.create_paginated_query(query_builder.create_query("subject_type", "database_name"), query_params)

                query.assert_called_with("subject_type", "database_name")
                elasticUtilsMock.order_by.assert_called_with("-field_name_to_order_by_value")

    def test_should_create_paginated_query_with_given_paginated_parameters(self):
        with patch("datawinners.search.query.elasticutils") as elasticUtilsMock:
            with patch("datawinners.search.query.QueryBuilder.create_query") as query:
                query.return_value = elasticUtilsMock
                elasticUtilsMock.order_by.return_value = elasticUtilsMock
                query_params = {
                    "start_result_number": 1,
                    "number_of_results": 10,
                    "order": "-",
                    "order_field": "field_name_to_order_by"
                }

                query_builder = QueryBuilder()
                query_builder.create_paginated_query(query_builder.create_query("subject_type", "database_name"), query_params)

                elasticUtilsMock.__getitem__.assert_called_with(slice(1, 11, None))

    def test_should_return_match_all_query_when_no_query_text_present(self):
        searchMock = Mock()
        query_text = ""
        searchMock.query.return_value = searchMock

        actual_query = QueryBuilder().add_query_criteria([], query_text, searchMock)

        searchMock.query.assert_called_with()
        self.assertEquals(actual_query, searchMock)

    def test_should_return_escaped_query_for_given_search_fields_when_query_text_present(self):
        searchMock = Mock()
        query_text = "query_text"

        with patch("datawinners.search.query.ElasticUtilsHelper") as elastic_utils_helper:
            elastic_utils_helper.return_value = elastic_utils_helper
            elastic_utils_helper.replace_special_chars.return_value = "query_text_escaped"

            QueryBuilder().add_query_criteria(["query_field1", "query_field2"], query_text, searchMock)

            elastic_utils_helper.replace_special_chars.assert_called_with('query_text')
            searchMock.query_raw.assert_called_with({
                "query_string": {
                    "fields": ("query_field1", "query_field2"),
                    "query": "query_text_escaped"
                }
            })

class TestElasticUtilsHelper(TestCase):
    def test_should_escape_special_characters(self):
        text = 'sho\uld_change_+-!^(){}[]~*?:"should_not_change__e#$__change_this&&that||thus'
        result = ElasticUtilsHelper().replace_special_chars(text)
        expected = 'sho\\\\uld_change_\\+\\-\\!\\^\\(\\)\\{\\}\\[\\]\\~\\*\\?\\:\\"should_not_change__e#$__change_this\\&&that\\||thus'
        self.assertEquals(result, expected)

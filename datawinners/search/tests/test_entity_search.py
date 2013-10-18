from unittest import TestCase
from mock import patch, Mock, MagicMock
from datawinners.search.entity_search import ElasticUtilsHelper, EntityQueryBuilder, SubjectQueryResponseCreator, SubjectQuery
from datawinners.search.entity_search import DatasenderQueryResponseCreator


class TestElasticUtilsHelper(TestCase):
    def test_should_escape_special_characters(self):
        text = 'sho\uld_change_+-!^(){}[]~*?:"should_not_change__e#$__change_this&&that||thus'
        result = ElasticUtilsHelper().replace_special_chars(text)
        expected = 'sho\\\\uld_change_\\+\\-\\!\\^\\(\\)\\{\\}\\[\\]\\~\\*\\?\\:\\"should_not_change__e#$__change_this\\&&that\\||thus'
        self.assertEquals(result, expected)


class TestEntityQueryBuilder(TestCase):
    def test_should_create_query_with_given_search_url(self):
        with patch("datawinners.search.entity_search.elasticutils") as elasticUtilsMock:
            with patch("datawinners.search.entity_search.ELASTIC_SEARCH_URL") as searchUrl:
                elasticUtilsMock.S.return_value = elasticUtilsMock

                EntityQueryBuilder().create_query("subject_type", "database_name")

                elasticUtilsMock.S.assert_called_with()
                elasticUtilsMock.es.assert_called_with(urls=searchUrl)

    def test_should_create_query_with_index_as_given_database_name(self):
        with patch("datawinners.search.entity_search.elasticutils") as elasticUtilsMock:
            elasticUtilsMock.S.return_value = elasticUtilsMock
            elasticUtilsMock.es.return_value = elasticUtilsMock

            EntityQueryBuilder().create_query("entity_type", "database_name")

            elasticUtilsMock.indexes.assert_called_with("database_name")

    def test_should_create_query_with_document_type_as_given_subject_type(self):
        with patch("datawinners.search.entity_search.elasticutils") as elasticUtilsMock:
            elasticUtilsMock.S.return_value = elasticUtilsMock
            elasticUtilsMock.es.return_value = elasticUtilsMock
            elasticUtilsMock.indexes.return_value = elasticUtilsMock

            EntityQueryBuilder().create_query("subject_type", "database_name")

            elasticUtilsMock.doctypes.assert_called_with("subject_type")

    def test_should_filter_query_with_only_non_void_documents(self):
        with patch("datawinners.search.entity_search.elasticutils") as elasticUtilsMock:
            elasticUtilsMock.S.return_value = elasticUtilsMock
            elasticUtilsMock.es.return_value = elasticUtilsMock
            elasticUtilsMock.indexes.return_value = elasticUtilsMock
            elasticUtilsMock.doctypes.return_value = elasticUtilsMock

            EntityQueryBuilder().create_query("subject_type", "database_name")

            elasticUtilsMock.filter.assert_called_with(void=False)

    def test_should_create_ordered_query_with_given_order_parameters(self):
        with patch("datawinners.search.entity_search.elasticutils") as elasticUtilsMock:
            with patch("datawinners.search.entity_search.EntityQueryBuilder.create_query") as query:
                query.return_value = elasticUtilsMock
                query_params = {
                    "start_result_number": 1,
                    "number_of_results": 10,
                    "order": "-",
                    "order_field": "field_name_to_order_by"
                }

                EntityQueryBuilder().create_paginated_query("subject_type", "database_name", query_params)

                query.assert_called_with("subject_type", "database_name")
                elasticUtilsMock.order_by.assert_called_with("-field_name_to_order_by_value")

    def test_should_create_paginated_query_with_given_paginated_parameters(self):
        with patch("datawinners.search.entity_search.elasticutils") as elasticUtilsMock:
            with patch("datawinners.search.entity_search.EntityQueryBuilder.create_query") as query:
                query.return_value = elasticUtilsMock
                elasticUtilsMock.order_by.return_value = elasticUtilsMock
                query_params = {
                    "start_result_number": 1,
                    "number_of_results": 10,
                    "order": "-",
                    "order_field": "field_name_to_order_by"
                }

                EntityQueryBuilder().create_paginated_query("subject_type", "database_name", query_params)

                elasticUtilsMock.__getitem__.assert_called_with(slice(1, 11, None))

    def test_should_return_match_all_query_when_no_query_text_present(self):
        searchMock = Mock()
        query_text = ""
        searchMock.query.return_value = searchMock

        actual_query = EntityQueryBuilder().add_query_criteria([], query_text, searchMock)

        searchMock.query.assert_called_with()
        self.assertEquals(actual_query, searchMock)

    def test_should_return_escaped_query_for_given_search_fields_when_query_text_present(self):
        searchMock = Mock()
        query_text = "query_text"

        with patch("datawinners.search.entity_search.ElasticUtilsHelper") as elastic_utils_helper:
            elastic_utils_helper.return_value = elastic_utils_helper
            elastic_utils_helper.replace_special_chars.return_value = "query_text_escaped"

            EntityQueryBuilder().add_query_criteria(["query_field1", "query_field2"], query_text, searchMock)

            elastic_utils_helper.replace_special_chars.assert_called_with('query_text')
            searchMock.query_raw.assert_called_with({
                "query_string": {
                    "fields": ("query_field1", "query_field2"),
                    "query": "query_text_escaped"
                }
            })


class TestSubjectQueryResponseCreator(TestCase):
    def test_should_return_subjects_with_field_values_for_specified_field_names_from_query_response(self):
        query = Mock()

        query.values_dict.return_value = [{
                                              "field_name1": "field_value11",
                                              "field_name2": "field_value12"
                                          }, {
                                              "field_name1": "field_value21",
                                              "field_name2": "field_value22"
                                          }]

        actualSubjects = SubjectQueryResponseCreator().create_response(
            required_field_names=["field_name1", "field_name2"], query=query)

        query.values_dict.assert_called_with(("field_name1", "field_name2"))
        self.assertEquals(actualSubjects, [["field_value11", "field_value12"], ["field_value21", "field_value22"]])

class TestDatasenderQueryResponseCreator(TestCase):
    def test_should_return_datasender_with_field_values_specified(self):
        required_field_names = ['field_name1', 'field_name2']
        query = Mock()
        query.values_dict.return_value = [{
                                      "field_name1": "field_value11",
                                      "field_name2": "field_value12"
                                  }, {
                                      "field_name1": "field_value21",
                                      "field_name2": "field_value22"
                                  }]


        datasenders = DatasenderQueryResponseCreator().create_response(required_field_names, query)
        query.values_dict.assert_called_with(("field_name1", "field_name2"))
        self.assertEquals(datasenders, [["field_value11", "field_value12"], ["field_value21", "field_value22"]])

    def test_should_return_datasender_with_space_seperated_projects(self):
        required_field_names = ['field_name1', 'projects']
        query = Mock()
        query.values_dict.return_value = [{
                                      "field_name1": "field_value11",
                                      "projects": ["p1","p2"]
                                  }, {
                                      "field_name1": "field_value21",
                                      "projects": ["p1", "p2", "p3"]
                                  }]


        datasenders = DatasenderQueryResponseCreator().create_response(required_field_names, query)
        query.values_dict.assert_called_with(("field_name1", "projects"))
        self.assertEquals(datasenders, [["field_value11", "p1, p2"], ["field_value21", "p1, p2, p3"]])

    def test_add_check_symbol_for_datasender_row(self):
        result = []
        check_img = '<img alt="Yes" src="/media/images/right_icon.png" class="device_checkmark">'
        datasender = {'email': 'test@test.com'}
        DatasenderQueryResponseCreator().add_check_symbol_for_row(datasender,result)
        self.assertListEqual(result, [check_img + check_img + check_img])

    def test_should_not_add_check_symbol_if_no_email_id(self):
        result = []
        check_img = '<img alt="Yes" src="/media/images/right_icon.png" class="device_checkmark">'
        datasender = {'name': 'name'}
        DatasenderQueryResponseCreator().add_check_symbol_for_row(datasender,result)
        self.assertListEqual(result, [check_img])

class TestSubjectQuery(TestCase):
    def test_should_return_all_subjects_matching_given_subject_type_and_database_name_and_query_text(self):
        user = Mock()
        subject_query_builder = Mock()
        subject_query = SubjectQuery()
        response_creator = Mock()
        subject_query.query_builder = subject_query_builder
        subject_query.response_creator = response_creator
        with patch("datawinners.search.entity_search.get_database_manager") as database_manager:
            with patch("datawinners.search.entity_search.header_fields") as header_fields:
                database_manager.return_value.database_name = "database_name"
                subject_headers = ["field1", "field2"]
                count_of_all_matching_results = 100
                header_fields.return_value.keys.return_value = subject_headers
                query_all_results = Mock()
                query = MagicMock()
                subject_query_builder.create_query.return_value = query
                query.count.return_value = count_of_all_matching_results
                query.__getitem__.return_value = query_all_results
                query_with_criteria = Mock()
                subject_query_builder.add_query_criteria.return_value = query_with_criteria
                response_creator.create_response.return_value = "expected subjects"

                actualSubjects = subject_query.query(user, "subject_type", "query_text")

                subject_query_builder.create_query.assert_called_once_with("subject_type", "database_name")
                query.__getitem__assert_called_with(slice(None, count_of_all_matching_results, None))
                subject_query_builder.add_query_criteria.assert_called_with(subject_headers, "query_text",
                                                                            query_all_results)
                response_creator.create_response.assert_called_with(subject_headers, query_with_criteria)
                self.assertEquals(actualSubjects, "expected subjects")

    def test_should_return_subjects_in_a_paginated_fashion_matching_given_subject_type_and_database_name_and_query_text(
            self):
        user = Mock()
        subject_query_builder = Mock()
        subject_query = SubjectQuery()
        response_creator = Mock()
        subject_query.query_builder = subject_query_builder
        subject_query.response_creator = response_creator
        with patch("datawinners.search.entity_search.get_database_manager") as database_manager:
            with patch("datawinners.search.entity_search.header_fields") as header_fields:
                database_manager.return_value.database_name = "database_name"
                subject_headers = ["field1", "field2"]
                header_fields.return_value.keys.return_value = subject_headers
                paginated_query = Mock()
                expected_total_result_count = 100
                paginated_query.count.return_value = expected_total_result_count
                subject_query_builder.create_paginated_query.return_value = paginated_query
                query_with_criteria = Mock()
                expected_filtered_result_count = 50
                query_with_criteria.count.return_value = expected_filtered_result_count
                subject_query_builder.add_query_criteria.return_value = query_with_criteria
                response_creator.create_response.return_value = "expected subjects"
                query_params = {
                    "start_result_number": 2,
                    "number_of_results": 10,
                    "order_by": 1,
                    "order": "-",
                    "search_text": "query_text"
                }

                filtered_count, total_count, actualSubjects = subject_query.paginated_query(user, "subject_type",
                                                                                            query_params)

                subject_query_builder.create_paginated_query.assert_called_once_with("subject_type", "database_name", {
                    "start_result_number": 2,
                    "number_of_results": 10,
                    "order_field": "field2",
                    "order": "-"
                })
                response_creator.create_response.assert_called_with(subject_headers, query_with_criteria)
                subject_query_builder.add_query_criteria.assert_called_with(subject_headers, "query_text",
                                                                            paginated_query)
                self.assertEquals(actualSubjects, "expected subjects")
                self.assertEquals(filtered_count, expected_filtered_result_count)
                self.assertEquals(total_count, expected_total_result_count)


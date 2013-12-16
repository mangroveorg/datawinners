from unittest import TestCase
from mock import patch, Mock, MagicMock
from datawinners.search.entity_search import SubjectQueryResponseCreator, SubjectQuery, DataSenderQueryBuilder
from datawinners.search.entity_search import DatasenderQueryResponseCreator


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
                                              "projects": ["p1", "p2"]
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
        DatasenderQueryResponseCreator().add_check_symbol_for_row(datasender, result)
        self.assertListEqual(result, [check_img + check_img + check_img])

    def test_should_not_add_check_symbol_if_no_email_id(self):
        result = []
        check_img = '<img alt="Yes" src="/media/images/right_icon.png" class="device_checkmark">'
        datasender = {'name': 'name'}
        DatasenderQueryResponseCreator().add_check_symbol_for_row(datasender, result)
        self.assertListEqual(result, [check_img])


class TestSubjectQuery(TestCase):
    def test_should_return_all_subjects_matching_given_subject_type_and_database_name_and_query_text(self):
        user = Mock()
        subject_query_builder = Mock()
        subject_query = SubjectQuery()
        response_creator = Mock()
        subject_query.query_builder = subject_query_builder
        subject_query.response_creator = response_creator
        with patch("datawinners.search.entity_search.SubjectQuery.get_headers") as header_fields:
            with patch("datawinners.search.entity_search.Query._getDatabaseName") as get_db_name:
                get_db_name.return_value = "database_name"
                subject_headers = ["field1", "field2"]
                count_of_all_matching_results = 100
                header_fields.return_value = subject_headers
                query_all_results = Mock()
                query = MagicMock()
                subject_query_builder.create_query.return_value = query
                query.count.return_value = count_of_all_matching_results
                query.__getitem__.return_value = query_all_results
                query_with_criteria = Mock()
                subject_query_builder.add_query_criteria.return_value = query_with_criteria
                response_creator.create_response.return_value = "expected subjects"

                actualSubjects = subject_query.query(user, "subject_type", "query_text")

                subject_query_builder.create_query.assert_called_once_with(doc_type='subject_type',
                                                                           database_name='database_name')
                query.__getitem__assert_called_with(slice(None, count_of_all_matching_results, None))
                subject_query_builder.add_query_criteria.assert_called_with(subject_headers, "query_text",
                                                                            query_all_results)
                response_creator.create_response.assert_called_with(subject_headers, query_with_criteria)
                self.assertEquals(actualSubjects, "expected subjects")

    def test_should_return_subjects_in_a_paginated_fashion_matching_given_subject_type_and_database_name_and_query_text(
            self):
        user = Mock()
        subject_query_builder = Mock()
        query_params = {
            "start_result_number": 2,
            "number_of_results": 10,
            "order_by": 1,
            "order": "-",
            "search_text": "query_text",
        }
        subject_query = SubjectQuery(query_params)
        response_creator = Mock()

        subject_query.query_builder = subject_query_builder
        subject_query.response_creator = response_creator
        with patch("datawinners.search.entity_search.SubjectQuery.get_headers") as header_fields:
            with patch("datawinners.search.entity_search.Query._getDatabaseName") as get_db_name:
                get_db_name.return_value = "database_name"
                subject_headers = ["field1", "field2"]
                header_fields.return_value = subject_headers
                paginated_query = Mock()
                expected_total_result_count = 100
                query = MagicMock()
                subject_query_builder.create_query.return_value = query

                paginated_query.count.return_value = expected_total_result_count
                subject_query_builder.create_paginated_query.return_value = paginated_query
                query_with_criteria = Mock()
                expected_filtered_result_count = 50
                query_with_criteria.count.return_value = expected_filtered_result_count
                subject_query_builder.add_query_criteria.return_value = query_with_criteria
                response_creator.create_response.return_value = "expected subjects"

                filtered_count, total_count, actualSubjects = subject_query.paginated_query(user, "subject_type")

                subject_query_builder.create_paginated_query.assert_called_once_with(query, {
                    "start_result_number": 2,
                    "number_of_results": 10,
                    "order_field": "field2",
                    "order": "-"
                })
                response_creator.create_response.assert_called_with(subject_headers, query_with_criteria)
                subject_query_builder.add_query_criteria.assert_called_with(subject_headers, "query_text",
                                                                            paginated_query, query_params=query_params)
                self.assertEquals(actualSubjects, "expected subjects")
                self.assertEquals(filtered_count, expected_filtered_result_count)
                self.assertEquals(total_count, expected_total_result_count)


class TestDataSenderQueryBuilder(TestCase):
    def test_should_add_not_filter_to_query(self):
        with patch("datawinners.search.entity_search.QueryBuilder") as query_builder:
            with patch("datawinners.search.query.elasticutils") as elasticUtilsMock:
                with patch("datawinners.search.entity_search.elasticutils.F") as mock_filter:
                    query_builder.return_value = query_builder
                    query_builder.create_query.return_value = elasticUtilsMock
                    mock_filter.return_value = mock_filter
                    DataSenderQueryBuilder().create_query("dbm")
                    query_builder.create_query.assert_called_with(database_name="dbm", doc_type="reporter")
                    elasticUtilsMock.filter.assert_called_with(~mock_filter)

from unittest import TestCase
from mock import patch, Mock, MagicMock
from datawinners.search.entity_search import SubjectQueryResponseCreator, SubjectQuery
from datawinners.search.entity_search import DatasenderQueryResponseCreator
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel


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

    def test_should_return_datasender_with_space_seperated_projects_and_groups(self):
        required_field_names = ['field_name1', 'projects']
        query = MagicMock()
        query.hits = [{
                                              "field_name1": "field_value11",
                                              "projects": ["p1", "p2"],
                                              "customgroups":["g1", "g2"]
                                          }, {
                                              "field_name1": "field_value21",
                                              "projects": ["p1", "p2", "p3"],
                                              "customgroups":["g2"]
                                          }]

        datasenders = DatasenderQueryResponseCreator().create_response(required_field_names, query)
        # query.values_dict.assert_called_with(("field_name1", "projects", "groups"))
        self.assertEquals(datasenders, [["field_value11", "p1, p2", "g1, g2", ""], ["field_value21", "p1, p2, p3", "g2", ""]])

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
                subject_query_builder.get_query.return_value = query
                query.count.return_value = count_of_all_matching_results
                query.__getitem__.return_value = query_all_results
                query_with_criteria = Mock()
                subject_query_builder.add_query_criteria.return_value = query_with_criteria
                response_creator.create_response.return_value = "expected subjects"

                actualSubjects = subject_query.query(user, "subject_type", "query_text")

                subject_query_builder.get_query.assert_called_once_with(doc_type='subject_type',
                                                                           database_name='database_name')
                query.__getitem__assert_called_with(slice(None, count_of_all_matching_results, None))
                subject_query_builder.add_query_criteria.assert_called_with(subject_headers, query_all_results,
                                                                            "query_text")
                response_creator.create_response.assert_called_with(subject_headers, query_with_criteria)
                self.assertEquals(actualSubjects, "expected subjects")

    def test_should_return_subjects_in_a_paginated_fashion_matching_given_subject_type_and_database_name_and_query_text(
            self):
        user = Mock()
        subject_query_builder = Mock()
        query_params = {
            "start_result_number": 2,
            "number_of_results": 10,
            "sort_field": 'last_name',
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
                subject_query_builder.get_query.return_value = query

                paginated_query.count.return_value = expected_total_result_count
                subject_query_builder.create_paginated_query.return_value = paginated_query
                query_with_criteria = Mock()
                expected_filtered_result_count = 50
                query_with_criteria.count.return_value = expected_filtered_result_count
                subject_query_builder.add_query_criteria.return_value = query_with_criteria
                response_creator.create_response.return_value = "expected subjects"

                filtered_count, total_count, actualSubjects = subject_query.paginated_query(user, "subject_type")

                subject_query_builder.create_paginated_query.assert_called_once_with(query, query_params)
                response_creator.create_response.assert_called_with(subject_headers, query_with_criteria)
                subject_query_builder.add_query_criteria.assert_called_with(subject_headers, paginated_query,
                                                                            "query_text", query_params=query_params)
                self.assertEquals(actualSubjects, "expected subjects")
                self.assertEquals(filtered_count, expected_filtered_result_count)
                self.assertEquals(total_count, expected_total_result_count)

    def test_should_return_form_id_appended_question_codes(self):
        subject_query = SubjectQuery()
        user = Mock()
        with patch('datawinners.search.entity_search.get_form_model_by_entity_type') as form_model:
            with patch('datawinners.search.entity_search.get_database_manager') as get_database_manager:
                with patch('datawinners.search.entity_search.header_fields') as header_fields:
                    header_fields.return_value = {'code1':'question1','code2':'question2'}
                    get_database_manager.return_value = Mock(spec=DatabaseManager)
                    form_model.return_value = Mock(spec=FormModel, id='form_id')

                    header_dict = subject_query.get_headers(user, 'subject_type')

                    expected = ['form_id_code1','form_id_code2']
                    self.assertEquals(header_dict,expected)

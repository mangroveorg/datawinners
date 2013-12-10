from collections import OrderedDict
import json
import unittest
from datetime import datetime
from django.http import HttpRequest

from mock import Mock, patch, call, PropertyMock, MagicMock

from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import EDITED_DATA_SUBMISSION
from datawinners.search.submission_query import SubmissionQuery
from framework.utils.database_manager_postgres import DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.form_model.field import TextField, IntegerField, SelectField, GeoCodeField, DateField
from mangrove.form_model.form_model import FormModel
from mangrove.transport.contract.survey_response import SurveyResponse, SurveyResponseDifference
from datawinners.project.helper import SUBMISSION_DATE_FORMAT_FOR_SUBMISSION
from datawinners.project.views.submission_views import build_static_info_context, get_option_value_for_field, construct_request_dict, get_survey_response_ids_from_request
from datawinners.project.views.submission_views import log_edit_action


class TestSubmissionViews(unittest.TestCase):
    def test_should_get_static_info_from_submission(self):
        with patch("datawinners.project.views.submission_views.get_data_sender") as get_data_sender:
            survey_response_document = SurveyResponseDocument(channel='web', status=False,
                                                              error_message="Some Error in submission")
            get_data_sender.return_value = ('Psub', 'rep2', 'tester@gmail.com')
            submission_date = datetime(2012, 02, 20, 12, 15, 44)
            survey_response_document.submitted_on = submission_date
            survey_response_document.created = datetime(2012, 02, 20, 12, 15, 50)

            survey_response = SurveyResponse(Mock())

            survey_response._doc = survey_response_document
            static_info = build_static_info_context(Mock(), survey_response)

            expected_values = OrderedDict({'static_content': {
                'Data Sender': ('Psub', 'rep2', 'tester@gmail.com'),
                'Source': u'Web',
                'Submission Date': submission_date.strftime(SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)}})
            expected_values.update({'is_edit': True})
            expected_values.update({'status': u'Error'})
            self.assertEqual(expected_values, static_info)

    def test_log_edit_of_existing_successful_submission(self):
        difference = SurveyResponseDifference(submitted_on=datetime(2013, 02, 23), status_changed=True)
        difference.changed_answers = {'q1': {'old': 23, 'new': 43}, 'q2': {'old': 'text2', 'new': 'correct text'},
                                      'q3': {'old': 'a', 'new': 'ab'}}
        original_survey_response = Mock(spec=SurveyResponse)
        edited_survey_response = Mock(spec=SurveyResponse)
        edited_survey_response.differs_from.return_value = difference
        project_name = 'project_name'
        request = Mock()

        form_model = Mock(spec=FormModel)
        int_field = IntegerField(name='question one', code='q1', label='question one', ddtype=Mock(spec=DataDictType))
        text_field = TextField(name='question two', code='q2', label='question two', ddtype=Mock(spec=DataDictType))
        choice_field = SelectField(name='question three', code='q3', label='question three',
                                   options=[("one", "a"), ("two", "b"), ("three", "c"), ("four", "d")],
                                   single_select_flag=False,
                                   ddtype=Mock(spec=DataDictType))
        form_model._get_field_by_code.side_effect = lambda x: {'q1': int_field, 'q2': text_field, 'q3': choice_field}[x]

        with patch('datawinners.project.views.submission_views.UserActivityLog') as activity_log:
            with patch(
                    'datawinners.project.views.submission_views.get_option_value_for_field') as get_option_value_for_field:
                get_option_value_for_field.return_value = {'old': u'one', 'new': u'one, two'}
                mock_log = Mock(spec=UserActivityLog)
                activity_log.return_value = mock_log
                log_edit_action(original_survey_response, edited_survey_response, request, project_name, form_model)
                expected_changed_answer_dict = {
                    'received_on': difference.created.strftime(SUBMISSION_DATE_FORMAT_FOR_SUBMISSION),
                    'status_changed': True,
                    'changed_answers': {'question one': {'old': 23, 'new': 43},
                                        'question two': {'old': 'text2', 'new': 'correct text'},
                                        'question three': {'old': u'one', 'new': u'one, two'}}}

                form_model._get_field_by_code.assert_calls_with([call('q1'), call('q2'), call('q3')])
                mock_log.log.assert_called_once_with(request, action=EDITED_DATA_SUBMISSION, project=project_name,
                                                     detail=json.dumps(expected_changed_answer_dict))

    def test_get_option_value_for_choice_fields(self):
        choices = {"old": "a", "new": "ab"}
        choice_field = SelectField(name='question', code='q1', label="question",
                                   options=[("one", "a"), ("two", "b"), ("three", "c"), ("four", "d")],
                                   single_select_flag=False,
                                   ddtype=Mock(spec=DataDictType))
        result_dict = get_option_value_for_field(choices, choice_field)
        expected = {"old": "one", "new": "one, two"}
        self.assertEqual(expected, result_dict)

    def test_get_option_value_for_other_field_changed_to_choice_fields(self):
        choices = {"old": "hi", "new": "ab"}
        choice_field = SelectField(name='question', code='q1', label="question",
                                   options=[("one", "a"), ("two", "b"), ("three", "c"), ("four", "d")],
                                   single_select_flag=False,
                                   ddtype=Mock(spec=DataDictType))
        result_dict = get_option_value_for_field(choices, choice_field)
        expected = {"old": "hi", "new": "one, two"}
        self.assertEqual(expected, result_dict)

    def test_convert_survey_response_values_to_dict_format(self):
        survey_response_doc = SurveyResponseDocument(
            values={'q1': '23', 'q2': 'sometext', 'q3': 'a', 'geo': '2.34,5.64', 'date': '12.12.2012'})
        survey_response = SurveyResponse(Mock())
        survey_response._doc = survey_response_doc
        int_field = IntegerField(name='question one', code='q1', label='question one', ddtype=Mock(spec=DataDictType))
        text_field = TextField(name='question two', code='q2', label='question two', ddtype=Mock(spec=DataDictType))
        single_choice_field = SelectField(name='question three', code='q3', label='question three',
                                          options=[("one", "a"), ("two", "b"), ("three", "c"), ("four", "d")],
                                          single_select_flag=True,
                                          ddtype=Mock(spec=DataDictType))
        geo_field = GeoCodeField(name='geo', code='GEO', label='geo', ddtype=Mock())
        date_field = DateField(name='date', code='DATE', label='date', date_format='dd.mm.yyyy', ddtype=Mock())
        questionnaire_form_model = Mock(spec=FormModel)
        questionnaire_form_model.form_code = 'test_form_code'
        questionnaire_form_model.fields = [int_field, text_field, single_choice_field, geo_field, date_field]

        request_dict = construct_request_dict(survey_response, questionnaire_form_model)
        expected_dict = OrderedDict({'q1': '23', 'q2': 'sometext', 'q3': 'a', 'GEO': '2.34,5.64', 'DATE': '12.12.2012',
                                     'form_code': 'test_form_code'})
        self.assertEqual(expected_dict, request_dict)

    def test_multiple_choice_field_should_be_split(self):
        survey_response_doc = SurveyResponseDocument(values={'q1': '23', 'q2': 'sometext', 'q3': 'ab'})
        survey_response = SurveyResponse(Mock())
        survey_response._doc = survey_response_doc
        int_field = IntegerField(name='question one', code='q1', label='question one', ddtype=Mock(spec=DataDictType))
        text_field = TextField(name='question two', code='q2', label='question two', ddtype=Mock(spec=DataDictType))
        choice_field = SelectField(name='question three', code='Q3', label='question three',
                                   options=[("one", "a"), ("two", "b"), ("three", "c"), ("four", "d")],
                                   single_select_flag=False,
                                   ddtype=Mock(spec=DataDictType))
        questionnaire_form_model = Mock(spec=FormModel)
        questionnaire_form_model.form_code = 'test_form_code'
        questionnaire_form_model.fields = [int_field, text_field, choice_field]

        result_dict = construct_request_dict(survey_response, questionnaire_form_model)
        expected_dict = {'q1': '23', 'q2': 'sometext', 'Q3': ['a', 'b'], 'form_code': 'test_form_code'}
        self.assertEqual(expected_dict, result_dict)

    def test_should_return_none_if_survey_response_questionnaire_is_different_from_form_model(self):
        survey_response_doc = SurveyResponseDocument(values={'q5': '23', 'q6': 'sometext', 'q7': 'ab'})
        survey_response = SurveyResponse(Mock())
        survey_response._doc = survey_response_doc
        int_field = IntegerField(name='question one', code='q1', label='question one', ddtype=Mock(spec=DataDictType))
        text_field = TextField(name='question two', code='q2', label='question two', ddtype=Mock(spec=DataDictType))
        choice_field = SelectField(name='question three', code='Q3', label='question three',
                                   options=[("one", "a"), ("two", "b"), ("three", "c"), ("four", "d")],
                                   single_select_flag=False,
                                   ddtype=Mock(spec=DataDictType))
        questionnaire_form_model = Mock(spec=FormModel)
        questionnaire_form_model.form_code = 'test_form_code'
        questionnaire_form_model.fields = [int_field, text_field, choice_field]
        result_dict = construct_request_dict(survey_response, questionnaire_form_model)
        expected_dict = {'q1': None, 'q2': None, 'Q3': None, 'form_code': 'test_form_code'}
        self.assertEqual(expected_dict, result_dict)

    def test_should_create_request_dict(self):
        survey_response_doc = SurveyResponseDocument(values={'q1': 23, 'q2': 'sometext', 'q3': 'ab'})
        survey_response = SurveyResponse(Mock())
        survey_response._doc = survey_response_doc
        int_field = IntegerField(name='question one', code='q1', label='question one', ddtype=Mock(spec=DataDictType))
        text_field = TextField(name='question two', code='q2', label='question two', ddtype=Mock(spec=DataDictType))
        choice_field = SelectField(name='question three', code='q3', label='question three',
                                   options=[("one", "a"), ("two", "b"), ("three", "c"), ("four", "d")],
                                   single_select_flag=False,
                                   ddtype=Mock(spec=DataDictType))
        questionnaire_form_model = Mock(spec=FormModel)
        questionnaire_form_model.form_code = 'test_form_code'
        questionnaire_form_model.fields = [int_field, text_field, choice_field]

        request_dict = construct_request_dict(survey_response, questionnaire_form_model)
        expected_dict = {'q1': 23, 'q2': 'sometext', 'q3': ['a', 'b'], 'form_code': 'test_form_code'}
        self.assertEqual(request_dict, expected_dict)

    def test_should_create_request_dict_with_older_survey_response(self):
        survey_response_doc = SurveyResponseDocument(values={'q1': 23, 'q2': 'sometext', 'q3': 'ab'})
        survey_response = SurveyResponse(Mock())
        survey_response._doc = survey_response_doc
        int_field = IntegerField(name='question one', code='q1', label='question one', ddtype=Mock(spec=DataDictType))
        text_field = TextField(name='question two', code='q2', label='question two', ddtype=Mock(spec=DataDictType))
        choice_field = SelectField(name='question three', code='q4', label='question three',
                                   options=[("one", "a"), ("two", "b"), ("three", "c"), ("four", "d")],
                                   single_select_flag=False,
                                   ddtype=Mock(spec=DataDictType))
        questionnaire_form_model = Mock(spec=FormModel)
        questionnaire_form_model.form_code = 'test_form_code'
        questionnaire_form_model.fields = [int_field, text_field, choice_field]

        request_dict = construct_request_dict(survey_response, questionnaire_form_model)
        expected_dict = {'q1': 23, 'q2': 'sometext', 'q4': None, 'form_code': 'test_form_code'}
        self.assertEqual(request_dict, expected_dict)

    def test_get_submission_ids_to_delete_should_give_back_selected_ids_if_select_all_flag_is_false(self):
        dbm = Mock(spec=DatabaseManager)
        request = Mock(spec=HttpRequest)
        post_params = {'id_list': json.dumps(['id1', 'id2'])}
        type(request).POST = PropertyMock(return_value=post_params)
        form_model = Mock(spec=FormModel)
        ids = get_survey_response_ids_from_request(dbm, request, form_model)
        self.assertEqual(ids, ['id1', 'id2'])

    def test_get_submission_ids_to_delete_should_call_submission_query_if_select_all_flag_is_true(self):
        dbm = MagicMock(spec=DatabaseManager)
        dbm.database_name = 'db_name'
        request = Mock(spec=HttpRequest)
        post_params = {"search_filters": json.dumps([]), "submission_type":"all",'all_selected': "true"}
        type(request).POST = PropertyMock(return_value=post_params)
        form_model = Mock(spec=FormModel)
        with patch('datawinners.project.views.submission_views.SubmissionQuery') as mock_submission_query:
            query_mock = Mock(spec=SubmissionQuery, name='SubmissionQueryInstance')
            mock_submission_query.return_value = query_mock
            query_mock.query.return_value = []
            get_survey_response_ids_from_request(dbm, request, form_model)
            mock_submission_query.assert_called_with(form_model, {'search_filters': []})
            query_mock.query.assert_called_with('db_name')

    def test_get_submission_ids_to_delete_should_call_submission_query_with_submission_type_if_select_all_flag_is_true(self):
        dbm = MagicMock(spec=DatabaseManager)
        dbm.database_name = 'db_name'
        request = Mock(spec=HttpRequest)
        post_params = {"search_filters": json.dumps([]), "submission_type":"success",'all_selected': "true"}
        type(request).POST = PropertyMock(return_value=post_params)
        form_model = Mock(spec=FormModel)
        with patch('datawinners.project.views.submission_views.SubmissionQuery') as mock_submission_query:
            query_mock = Mock(spec=SubmissionQuery, name='SubmissionQueryInstance')
            mock_submission_query.return_value = query_mock
            query_mock.query.return_value = []
            get_survey_response_ids_from_request(dbm, request, form_model)
            mock_submission_query.assert_called_with(form_model, {'search_filters': [], 'filter':'success'})
            query_mock.query.assert_called_with('db_name')
from collections import OrderedDict
import json
import unittest
from django.http import HttpRequest
from mock import Mock, patch, call
from activitylog.models import UserActivityLog
from common.constant import EDITED_DATA_SUBMISSION
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.documents import SubmissionLogDocument
from mangrove.form_model.field import TextField, IntegerField, SelectField
from mangrove.form_model.form_model import FormModel
from mangrove.transport.contract.submission import Submission
from mangrove.transport.contract.survey_response import SurveyResponse, SurveyResponseDifference
from mangrove.utils.dates import utcnow
from project.helper import SUBMISSION_DATE_FORMAT_FOR_SUBMISSION
from datawinners.project.views.submission_views import build_static_info_context, get_option_value_for_field
from datetime import  datetime
from datawinners.project.views.submission_views import  log_edit_action

class TestSubmissionViews(unittest.TestCase):

    def test_should_get_static_info_from_submission(self):
        with patch("datawinners.project.views.submission_views.get_data_sender") as get_data_sender:
            get_data_sender.return_value = ('Psub', 'rep2', 'tester@gmail.com')
            created_time = utcnow()
            submission_document = SubmissionLogDocument(source='tester@gmail.com', channel='web', status=False,
                event_time=created_time, error_message="Some Error in submission")
            submission = Submission(Mock())
            submission._doc = submission_document
            static_info = build_static_info_context(Mock(), Mock(spec=HttpRequest), submission)

            expected_values = OrderedDict({'static_content': {
                'Data Sender': ('Psub', 'rep2', 'tester@gmail.com'),
                'Source': u'Web',
                'Submission Date': created_time.strftime(SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)}})
            expected_values.update({'is_edit': True})
            expected_values.update({'status': u'Error. Some Error in submission'})
            self.assertEqual(expected_values, static_info)

    def test_log_edit_of_existing_successful_submission(self):
        difference = SurveyResponseDifference(created=datetime(2013, 02, 23), status_changed=True)
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
            options=[("one", "a"), ("two", "b"), ("three", "c"), ("four", "d")], single_select_flag=False,
            ddtype=Mock(spec=DataDictType))
        form_model._get_field_by_code.side_effect = lambda x: {'q1': int_field, 'q2': text_field, 'q3': choice_field}[x]

        with patch('datawinners.project.views.submission_views.UserActivityLog') as activity_log:
            with patch('datawinners.project.views.submission_views.get_option_value_for_field') as get_option_value_for_field:
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
            options=[("one", "a"), ("two", "b"), ("three", "c"), ("four", "d")], single_select_flag=False,
            ddtype=Mock(spec=DataDictType))
        result_dict = get_option_value_for_field(choices, choice_field)
        expected = {"old": "one", "new": "one, two"}
        self.assertEqual(expected,result_dict)

    def test_get_option_value_for_other_field_changed_to_choice_fields(self):
        choices = {"old": "hi", "new": "ab"}
        choice_field = SelectField(name='question', code='q1', label="question",
            options=[("one", "a"), ("two", "b"), ("three", "c"), ("four", "d")], single_select_flag=False,
            ddtype=Mock(spec=DataDictType))
        result_dict = get_option_value_for_field(choices, choice_field)
        expected = {"old": "hi", "new": "one, two"}
        self.assertEqual(expected,result_dict)


from collections import OrderedDict
import json
import unittest
from django.http import HttpRequest
from mock import Mock, patch, call
from activitylog.models import UserActivityLog
from common.constant import EDITED_DATA_SUBMISSION
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.documents import SubmissionLogDocument
from mangrove.form_model.field import TextField, IntegerField
from mangrove.form_model.form_model import FormModel
from mangrove.transport.contract.submission import Submission
from mangrove.transport.contract.survey_response import SurveyResponse, SurveyResponseDifference
from mangrove.utils.dates import utcnow
from project.helper import SUBMISSION_DATE_FORMAT_FOR_SUBMISSION
from datawinners.project.views.submission_views import build_static_info_context
from datetime import date, datetime
from project.views.submission_views import delete_submissions_by_ids
from datawinners.project.views.submission_views import  log_edit_action

class TestSubmissionViews(unittest.TestCase):
    def test_should_delete_submission_with_error_status(self):
        dbm = Mock()
        request = Mock()
        submission = Mock(spec=Submission)
        submission.created = date(2012, 8, 20)
        submission.data_record = None
        with patch("project.views.submission_views.Submission.get") as get_submission:
            get_submission.return_value = submission
            with patch("project.views.submission_views.get_organization") as get_organization:
                get_organization.return_value = Mock()
                received_times = delete_submissions_by_ids(dbm, request, ['1'])
                self.assertEqual(['20/08/2012 00:00:00'], received_times)

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
        difference.changed_answers = {'q1': {'old': 23, 'new': 43}, 'q2': {'old': 'text2', 'new': 'correct text'}}
        original_survey_response = Mock(spec=SurveyResponse)
        edited_survey_response = Mock(spec=SurveyResponse)
        edited_survey_response.differs_from.return_value = difference
        project_name = 'project_name'
        request = Mock()

        form_model = Mock(spec=FormModel)
        int_field = IntegerField(name='question one', code='q1', label='question one', ddtype=Mock(spec=DataDictType))
        text_field = TextField(name='question two', code='q2', label='question two', ddtype=Mock(spec=DataDictType))
        form_model._get_field_by_code.side_effect = lambda x: {'q1': int_field, 'q2': text_field}[x]

        with patch('datawinners.project.views.submission_views.UserActivityLog') as activity_log:
            mock_log = Mock(spec=UserActivityLog)
            activity_log.return_value = mock_log
            log_edit_action(original_survey_response, edited_survey_response, request, project_name, form_model)
            expected_changed_answer_dict = {
                'received_on': difference.created.strftime(SUBMISSION_DATE_FORMAT_FOR_SUBMISSION),
                'status_changed': True,
                'changed_answers': {'question one': {'old': 23, 'new': 43},
                                    'question two': {'old': 'text2', 'new': 'correct text'}}}


            form_model._get_field_by_code.assert_calls_with([call('q1'), call('q2')])
            mock_log.log.assert_called_once_with(request, action=EDITED_DATA_SUBMISSION, project=project_name,
                detail=json.dumps(expected_changed_answer_dict))


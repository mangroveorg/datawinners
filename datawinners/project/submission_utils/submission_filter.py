import unittest
from mock import Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from mangrove.transport import TransportInfo
from mangrove.transport.submissions import Submission
from project.filters import ReportPeriodFilter, SubjectFilter, SubmissionDateFilter, DataSenderFilter
from datawinners.questionnaire.helper import get_report_period_question_name_and_datetime_format

class SubmissionFilter(object):

    def __init__(self, params=None, form_model=None):
        self.filter_list = self._build_filters(params, form_model)

    def filter(self, submissions):
        if not self.filter_list:
            return submissions

        self.to_lowercase_submission_keys(submissions)

        for filter in self.filter_list:
            submissions = filter.filter(submissions)

        return submissions

    def to_lowercase_submission_keys(self, submissions):
        for submission in submissions:
            values = submission.values
            submission._doc.values = dict((k.lower(), v) for k,v in values.iteritems())

    def _build_filters(self, params, form_model):
        if not params:
            return []
        return filter(lambda x: x is not None,
        [self._build_report_period_filter(form_model, params.get('start_time', ""), params.get('end_time', "")),
         self._build_submission_date_filter(params.get('submission_date_start', ""), params.get('submission_date_end', "")),
         self._build_subject_filter(form_model.entity_question.code, params.get('subject_ids', "").strip()),
         self._build_datasender_filter(params.get('submission_sources', "").strip()),
         ])

    def _build_report_period_filter(self, form_model, start_time, end_time):
        if not start_time or not end_time:
            return None
        time_range = {'start': start_time, 'end': end_time}
        question_name, datetime_format = get_report_period_question_name_and_datetime_format(form_model)

        return ReportPeriodFilter(question_name, time_range, datetime_format)

    def _build_submission_date_filter(self, start_time, end_time):
        if not start_time or not end_time:
            return None
        time_range = {'start': start_time, 'end': end_time}
        return SubmissionDateFilter(time_range)

    def _build_subject_filter(self, entity_question_code, subject_ids):
        if not subject_ids.strip():
            return None
        return SubjectFilter(entity_question_code.lower(), subject_ids)


    def _build_datasender_filter(self, submission_sources):
        if not submission_sources.strip():
            return None
        return DataSenderFilter(submission_sources)


class SubmissionFilterTest(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.mock_form_model = Mock(spec=FormModel)
        self.mock_form_model.entity_question.code = '123'

        self.transport_info = TransportInfo('web', 'source', 'destination')
        self.values = [
            {'q1': 'q1', 'q2': '30.07.2012', '123': '001'},
            {'q1': 'q1', 'q2': '30.08.2012', '123': '005'},
            {'q1': 'q1', 'q2': '30.08.2012', '123': '002'},
            ]
        self.submissions = [
            Submission(self.dbm, transport_info=self.transport_info, form_code='test', values=self.values[0]),
            Submission(self.dbm, transport_info=self.transport_info, form_code='test', values=self.values[1]),
            Submission(self.dbm, transport_info=self.transport_info, form_code='test', values=self.values[2])
        ]

    def test_should_return_all_submission_if_filtering_with_no_filters(self):
        filtered_submissions = SubmissionFilter().filter(submissions=self.submissions)

        self.assertEqual(3, len(filtered_submissions))

    def test_should_return_submissions_that_filtered_by_filter_list(self):
        params = {'submission_date_start': '01.01.2013', 'submission_date_end': '30.01.2013', 'subject_ids': '005'}
        filtered_submissions = SubmissionFilter(params, self.mock_form_model).filter(submissions=self.submissions)
        self.assertEqual(1, len(filtered_submissions))

#    def test_should_return_submissions_that_filtered_by_subject_ids(self):
#            params = {'subject_ids': '006'}
#            filtered_submissions = SubmissionFilter(params, self.mock_form_model).filter(submissions=self.submissions)
#            self.assertEqual(1, len(filtered_submissions))





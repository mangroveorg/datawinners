import unittest
from mock import Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.transport.facade import TransportInfo
from mangrove.transport.submissions import Submission
from project.filters import ReportPeriodFilter, SubjectFilter
from project.views import *

class TestSubmissionFilters(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.transport_info = TransportInfo('web', 'source', 'destination')

    def test_should_return_empty_list_when_filtering_empty_submissions(self):
        submission_logs = []
        filtered_submission_logs = ReportPeriodFilter(question_name='q2').filter(submission_logs)
        self.assertEqual([], filtered_submission_logs)

    def test_should_raise_value_error_when_filtering_with_no_question_name(self):
        submission = Submission(self.dbm, self.transport_info, form_code='test',
            values={'q1': 'q1', 'q2': '30.06.2012'})
        self.assertRaises(AssertionError, ReportPeriodFilter(period={'start': '01.06.2012', 'end': '30.06.2012'}).filter
            , [submission])

    def test_should_return_submissions_within_reporting_period(self):
        submission_in_report_period = Submission(self.dbm, transport_info=self.transport_info, form_code='test',
            values={'q1': 'q1', 'q2': '30.07.2012'})
        submission_not_in_report_period = Submission(self.dbm, transport_info=self.transport_info, form_code='test',
            values={'q1': 'q1', 'q2': '30.08.2012'})
        submission_logs = [submission_in_report_period, submission_not_in_report_period]

        filtered_submission_logs = ReportPeriodFilter(question_name='q2',
            period={'start': '01.06.2012', 'end': '30.07.2012'}).filter(submission_logs)

        self.assertEquals([submission_in_report_period], filtered_submission_logs)

    def test_should_return_submissions_match_subject_ids(self):
        submission_reporting_on_subject_001 = Submission(self.dbm, transport_info=self.transport_info, form_code='test',
            values={'q1': 'q1', 'q2': '30.07.2012', 'entity_question_code': '001'})

        submission_reporting_on_subject_005 = Submission(self.dbm, transport_info=self.transport_info, form_code='test',
            values={'q1': 'q1', 'q2': '30.08.2012', 'entity_question_code': '005'})

        submission_not_reporting_on_any_query_subjects = Submission(self.dbm, transport_info=self.transport_info, form_code='test',
            values={'q1': 'q1', 'q2': '30.08.2012', 'entity_question_code': '002'})

        submission_logs = [submission_reporting_on_subject_001, submission_reporting_on_subject_005, submission_not_reporting_on_any_query_subjects]

        filtered_submissions = SubjectFilter("entity_question_code", '001,005').filter(submission_logs)

        self.assertEqual(2, len(filtered_submissions))

    def test_should_build_filter_by_subject(self):
        form_model = Mock()
        form_model.entity_question.code = '123'
        filters = build_filters({'subject_ids': 'subject'}, form_model)
        self.assertEqual(1, len(filters))
        self.assertIsInstance(filters[0], SubjectFilter)







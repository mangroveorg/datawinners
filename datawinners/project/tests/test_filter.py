import unittest
from mock import Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.transport.facade import TransportInfo
from mangrove.transport.submissions import Submission
from project.filters import ReportPeriodFilter

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
        self.assertRaises(AssertionError, ReportPeriodFilter(period={'start': '01.06.2012', 'end': '30.06.2012'}).filter, [submission])

    def test_should_return_submissions_within_reporting_period(self):
        submission_in_report_period = Submission(self.dbm, transport_info=self.transport_info, form_code='test',
            values={'q1': 'q1', 'q2': '30.07.2012'})
        submission_not_in_report_period = Submission(self.dbm, transport_info=self.transport_info, form_code='test',
            values={'q1': 'q1', 'q2': '30.08.2012'})
        submission_logs = [submission_in_report_period, submission_not_in_report_period]

        filtered_submission_logs = ReportPeriodFilter(question_name='q2', period={'start': '01.06.2012', 'end': '30.07.2012'}).filter(submission_logs)

        self.assertEquals([submission_in_report_period], filtered_submission_logs)





        


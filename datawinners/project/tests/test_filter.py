import unittest
from mock import Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.transport.facade import TransportInfo
from mangrove.transport.submissions import Submission
from project.filters import ReportPeriodFilter, SubjectFilter, DataSenderFilter
from project.views import *

class TestSubmissionFilters(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.transport_info = TransportInfo('web', 'source', 'destination')
        self.values = [
            {'q1': 'q1', 'q2': '30.07.2012', 'entity_question_code': '001'},
            {'q1': 'q1', 'q2': '30.08.2012', 'entity_question_code': '005'},
            {'q1': 'q1', 'q2': '30.08.2012', 'entity_question_code': '002'}
        ]
        self.submissions = [
            Submission(self.dbm, self.transport_info, form_code='test', values=self.values[0]),
            Submission(self.dbm, transport_info=self.transport_info, form_code='test', values=self.values[1]),
            Submission(self.dbm, transport_info=self.transport_info, form_code='test', values=self.values[2])
        ]

    def test_should_return_empty_list_when_filtering_empty_submissions(self):
        submission_logs = []
        filtered_submission_logs = ReportPeriodFilter(question_name='q2', period={'start': '01.06.2012', 'end': '30.06.2012'}).filter(submission_logs)
        self.assertEqual([], filtered_submission_logs)

    def test_should_raise_value_error_when_filtering_with_no_question_name(self):
        self.assertRaises(AssertionError, ReportPeriodFilter(period={'start': '01.07.2012', 'end': '30.07.2012'}).filter, [self.submissions[0]])

    def test_should_return_submissions_within_reporting_period(self):
        submission_in_report_period = self.submissions[0]
        submission_not_in_report_period = self.submissions[1]
        submission_logs = [submission_in_report_period, submission_not_in_report_period]

        filtered_submission_logs = ReportPeriodFilter(question_name='q2',
            period={'start': '01.06.2012', 'end': '30.07.2012'}).filter(submission_logs)

        self.assertEquals([submission_in_report_period], filtered_submission_logs)

    def test_should_return_submissions_match_subject_ids(self):
        submission_reporting_on_subject_001 = self.submissions[0]

        submission_reporting_on_subject_005 = self.submissions[1]

        submission_not_reporting_on_any_query_subjects = self.submissions[2]

        submission_logs = [submission_reporting_on_subject_001, submission_reporting_on_subject_005, submission_not_reporting_on_any_query_subjects]

        filtered_submissions = SubjectFilter("entity_question_code", '001,005').filter(submission_logs)

        self.assertEqual(2, len(filtered_submissions))

    def test_should_build_filter_by_subject(self):
        form_model = Mock()
        form_model.entity_question.code = '123'
        filters = build_filters({'subject_ids': 'subject'}, form_model)
        self.assertEqual(1, len(filters))
        self.assertIsInstance(filters[0], SubjectFilter)

    def test_should_build_filter_by_datasender(self):
        form_model = Mock()
        form_model.entity_question.code = '123'
        filters = build_filters({'submission_sources': 'tester150411@gmail.com'}, form_model)
        self.assertEqual(1, len(filters))
        self.assertIsInstance(filters[0], DataSenderFilter)

    def test_should_return_submissions_filter_by_datasender(self):
        submission_logs = [
            Submission(self.dbm,transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'), form_code='test',values=self.values[0]),
            Submission(self.dbm, transport_info=TransportInfo('web', '127359085', 'destination'), form_code='test',values=self.values[1]),
            Submission(self.dbm, transport_info=TransportInfo('web', '0000000000', 'destination'), form_code='test',values=self.values[2])
        ]

        filtered_submissions = DataSenderFilter('tester150411@gmail.com').filter(submission_logs)
        self.assertEqual(1, len(filtered_submissions))

    def test_should_return_empty_submission_list_when_no_matching_datasender_found(self):
        submission_logs = [
            Submission(self.dbm,transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'), form_code='test',values=self.values[0]),
            Submission(self.dbm, transport_info=TransportInfo('web', '127359085', 'destination'), form_code='test',values=self.values[1]),
            Submission(self.dbm, transport_info=TransportInfo('web', '0000000000', 'destination'), form_code='test',values=self.values[2])
        ]

        filtered_submissions = DataSenderFilter('no_matching_datasender').filter(submission_logs)
        self.assertEqual(0, len(filtered_submissions))

    def test_should_return_submissions_filter_by_test_datasender(self):
        test_submission1 = Submission(self.dbm, transport_info=TransportInfo('web', '127359085', 'destination'),
            form_code='test', values=self.values[1])
        test_submission1._doc.test = True

        test_submission2 = Submission(self.dbm, transport_info=TransportInfo('web', '0000000000', 'destination'),
            form_code='test', values=self.values[2])
        test_submission2._doc.test = False

        submission_logs = [
            Submission(self.dbm,transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'), form_code='test',values=self.values[0]),
            test_submission1,
            test_submission2
        ]

        filtered_submissions = DataSenderFilter('TEST').filter(submission_logs)
        self.assertEqual(1, len(filtered_submissions))

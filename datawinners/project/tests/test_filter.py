import unittest
from mock import Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.transport.facade import TransportInfo
from mangrove.transport.submissions import Submission
from project.filters import ReportPeriodFilter, SubjectFilter, DataSenderFilter, SubmissionDateFilter
from project.views import *


class TestSubmissionFilters(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.mock_form_model = Mock(spec=FormModel)
        self.mock_form_model.entity_question.code = '123'
        self.transport_info = TransportInfo('web', 'source', 'destination')
        self.values = [
            {'q1': 'q1', 'q2': '30.07.2012', 'entity_question_code': '001'},
            {'q1': 'q1', 'q2': '30.08.2012', 'entity_question_code': '005'},
            {'q1': 'q1', 'q2': '30.08.2012', 'entity_question_code': '002'},
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

    def test_should_remove_submissions_whose_reporting_period_does_not_match_date_format(self):
        submission_logs_with_wrong_date_format = [
            Submission(self.dbm, self.transport_info, form_code='test',values={'q1': 'q1', 'q2': '12.25.2012', 'entity_question_code': '001'}),
            Submission(self.dbm, self.transport_info, form_code='test',values={'q1': 'q1', 'q2': '12.2012', 'entity_question_code': '001'})
        ]

        self.submissions.extend(submission_logs_with_wrong_date_format)
        filtered_submission_logs = ReportPeriodFilter(question_name='q2', period={'start': '01.05.2012', 'end': '30.09.2012'}).filter(self.submissions)
        self.assertEqual(len(filtered_submission_logs), 3)

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
        filters = build_filters({'subject_ids': 'subject'}, self.mock_form_model)
        self.assertEqual(1, len(filters))
        self.assertIsInstance(filters[0], SubjectFilter)

    def test_should_build_filter_by_datasender(self):
        filters = build_filters({'submission_sources': 'tester150411@gmail.com'}, self.mock_form_model)
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

    def test_should_build_filter_by_submission_date(self):
        filters = build_filters({'submission_date_start': '01.08.2012', 'submission_date_end': '31.08.2012'}, self.mock_form_model)
        self.assertEqual(1, len(filters))
        self.assertIsInstance(filters[0], SubmissionDateFilter)

    def test_should_return_submissions_within_submission_date(self):
        submission1 = self.submissions[0]
        submission1._doc.created = datetime.date(2012, 8, 15)

        submission2 = self.submissions[1]
        submission2._doc.created = datetime.date(2012, 8, 27)

        submission3 = self.submissions[2]
        submission3._doc.created = datetime.date(2012, 8, 3)

        submission_logs = [submission1, submission2, submission3]

        filtered_submission_logs = SubmissionDateFilter(
            period={'start': '10.08.2012', 'end': '31.08.2012'}).filter(submission_logs)

        self.assertEquals(submission_logs[:2], filtered_submission_logs)

    def test_should_build_filter_by_keyword(self):
        raw_field_values = [('Test', u'cid001'), '25.12.2012', u'20.09.2012', ('N/A', None, u'261333745261'), 'sms', '40', ['O+'], ['Rapid weight loss', 'Dry cough'], '-18.1324,27.6547'],\
                           [('Test', u'cid001'), '25.12.2012', u'20.09.2012', ('TEST', '', 'TEST'), 'test', '40', ['O+'], ['Rapid weight loss', 'Dry cough'], '-18.1324,27.6547'],\
                           [('Test', u'cid001'), '25.12.2011', u'20.09.2012', (u'Tester Pune', 'admin', u'tester150411@gmail.com'), 'admin', '40.0', ['AB'], ['Rapid weight loss'], '18.1324,27.6547']

        filtered_field_values = filter_by_keyword('sms'.strip(), raw_field_values)

        self.assertEquals(len(filtered_field_values), 1)
        self.assertEquals(filtered_field_values[0], raw_field_values[0])

    def test_should_filter_for_other_reporting_date_format(self):
        submission_logs_with_wrong_date_format = [
            Submission(self.dbm, self.transport_info, form_code='test',values={'q1': 'q1', 'q2': '12.25.2012', 'entity_question_code': '001'}),
            Submission(self.dbm, self.transport_info, form_code='test',values={'q1': 'q1', 'q2': '12.2012', 'entity_question_code': '001'})
        ]

        self.submissions.extend(submission_logs_with_wrong_date_format)
        filtered_submission_logs = ReportPeriodFilter(question_name='q2', period={'start': '05.01.2012', 'end': '12.30.2012'}, date_format="mm.dd.yyyy").filter(self.submissions)
        self.assertEqual(len(filtered_submission_logs), 1)

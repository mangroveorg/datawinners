import unittest
from mock import Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.transport import TransportInfo
from mangrove.transport.submissions import Submission
from project.filters import ReportPeriodFilter, SubjectFilter

class SubmissionFilter(object):

    def __init__(self, filter_list):
        self.filter_list = filter_list

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

class SubmissionFilterTest(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
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

    def test_should_return_all_submission_if_filtering_with_no_filters(self):
        filter_list = []

        filtered_submissions = SubmissionFilter(filter_list).filter(submissions=self.submissions)

        self.assertEqual(3, len(filtered_submissions))

    def test_should_return_submissions_that_filtered_by_filter_list(self):
        filter_list = [ReportPeriodFilter(question_name='q2', period={'start': '01.08.2012', 'end': '30.09.2012'}), SubjectFilter("entity_question_code", '001,005')]
        filtered_submissions = SubmissionFilter(filter_list).filter(submissions=self.submissions)
        self.assertEqual(1, len(filtered_submissions))



import unittest
from mock import   PropertyMock, patch
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from mangrove.transport import TransportInfo
from mangrove.transport.submissions import Submission
from project.submission_list import SubmissionList

class TestSubmissionData(unittest.TestCase):
    def setUp(self):
        self.form_model = PropertyMock(return_value=FormModel)
        self.manager = PropertyMock(return_value=DatabaseManager)
        self.filters = {u"name": "abcd"}

    def test_should_get_subject_list(self):
        submission_list = SubmissionList(self.form_model, self.manager, "org_id", "success", self.filters)
        submission_list._subject_list = [('Clinic-Two', u'cli16'), ('Clinic-One', u'cli15')]
        subject_list = submission_list.get_subjects()
        expected = [('Clinic-One', u'cli15'), ('Clinic-Two', u'cli16')]
        self.assertEqual(expected, subject_list)

    def test_should_get_data_sender_list(self):
        with patch("datawinners.project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            get_submissions.return_value = [
                Submission(self.manager, transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                    form_code="cli001", values={"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})]
        submission_list = SubmissionList(self.form_model, self.manager, "org_id", "success", self.filters)
        submission_list._data_senders = [('Tester Pune', 'admin', 'tester150411@gmail.com')]
        data_sender_list = submission_list.get_data_senders()
        expected = [('Tester Pune', 'admin', 'tester150411@gmail.com')]
        self.assertEqual(expected, data_sender_list)


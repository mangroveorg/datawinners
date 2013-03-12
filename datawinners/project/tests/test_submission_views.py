import unittest
from django.http import HttpRequest
from mock import Mock, patch
from mangrove.datastore.documents import SubmissionLogDocument
from mangrove.transport.submissions import Submission
from mangrove.utils.dates import utcnow
from project.views.submission_views import build_static_info_context

class TestSubmissionViews(unittest.TestCase):
    def test_should_get_static_info_from_submission(self):
        with patch("project.views.submission_views.get_data_sender") as get_data_sender:
            get_data_sender.return_value = ('Psub', 'rep2', 'tester@gmail.com')
            created_time = utcnow()
            temp_dict = {}
            submission_document = SubmissionLogDocument(source='tester@gmail.com', channel='web', status=False,
                event_time=created_time,error_message="Some Error in submission")
            submission = Submission(Mock())
            submission._doc = submission_document
            build_static_info_context(temp_dict, Mock(), Mock(spec=HttpRequest), submission)
            SUBMISSION_DATE_FORMAT = "%b. %d, %Y, %I:%M %p"
            expected_values = {'channel': 'web',
                               'status': 'Error',
                               'created': created_time.strftime(SUBMISSION_DATE_FORMAT),
                               'data_sender': ('Psub', 'rep2', 'tester@gmail.com'),
                               'is_edit': True,
                               'errors':'Some Error in submission'
                               }
            self.assertEqual(expected_values, temp_dict)

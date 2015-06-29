from unittest import TestCase
from mock import MagicMock
from datawinners.project.views.poll_views import _construct_poll_recipients


class TestProject(TestCase):

    def test_should_construct_poll_recipients_map_name_and_rep_id(self):
        poll_submissions = MagicMock()
        poll_submissions.recipients = '["Ds1(rep1)", "Ds2(rep2)"]'

        poll_recipients_map = _construct_poll_recipients(poll_submissions)

        expected = {'Ds1': 'rep1',  'Ds2': 'rep2'}

        self.assertDictEqual(expected, poll_recipients_map)


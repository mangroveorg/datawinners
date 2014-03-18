from unittest import TestCase
from mock import Mock, MagicMock
from datawinners.project.submission.submission_import import SubmissionImporter


class TestSubmissionImporter(TestCase):

    def test_should_update_datasender_id_with_logged_in_user_for_a_project_submitted_by_a_non_user(self):

        submission_importer = SubmissionImporter(None, None, None, None, None, None)

        rows = [{},{}]
        user_profile = MagicMock()
        user_profile.reporter_id = 'rep123'
        submission_importer._add_reporter_id_for_datasender(parsed_rows=rows, user_profile=user_profile,
                                                            is_organization_user=False)

        self.assertEquals(rows[0]['eid'], 'rep123')
        self.assertEquals(rows[1]['eid'], 'rep123')


    def test_should_not_update_datasender_id_with_logged_in_user_for_a_project_submitted_by_a_user(self):

        submission_importer = SubmissionImporter(None, None, None, None, None, None)

        rows = [{'eid':'rep14'},{'eid':'rep276'}]
        user_profile = MagicMock()
        user_profile.reporter_id = 'rep123'
        submission_importer._add_reporter_id_for_datasender(parsed_rows=rows, user_profile=user_profile,
                                                            is_organization_user=True)

        self.assertEquals(rows[0]['eid'], 'rep14')
        self.assertEquals(rows[1]['eid'], 'rep276')

    def test_should_update_datasender_id_with_logged_in_user_for_a_project_submitted_by_a_user_with_no_explicit_datasender_entry(self):

        submission_importer = SubmissionImporter(None, None, None, None, None, None)

        rows = [{'eid':''},{'eid':'rep276'}]
        user_profile = MagicMock()
        user_profile.reporter_id = 'rep123'
        submission_importer._add_reporter_id_for_datasender(parsed_rows=rows, user_profile=user_profile,
                                                            is_organization_user=True)

        self.assertEquals(rows[0]['eid'], 'rep123')
        self.assertEquals(rows[1]['eid'], 'rep276')
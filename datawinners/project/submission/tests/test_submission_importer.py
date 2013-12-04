from unittest import TestCase
from mock import patch, Mock, MagicMock
from datawinners.project.submission.submission_import import SubmissionPersister


class TestSubmissionImporter(TestCase):
    pass

class TestSubmissionPersister(TestCase):

    def setUp(self):
        pass

    def test_should_save_submissions_when_the_limit_not_exceeded(self):
        with patch("datawinners.project.submission.submission_import.Organization") as Organization:
            organization = MagicMock()
            Organization.objects.get.return_value= organization
            organization.has_exceeded_submission_limit.return_value = False
            user_profile = MagicMock()
            valid_rows = [{"key":"value1"}, {"key":"value2"}]
            with patch("datawinners.project.submission.submission_import.SurveyResponseService") as SurveyResponseService:
                service, project, user, form_model = Mock(), Mock(), Mock(), Mock()
                SurveyResponseService.return_value = service
                project.is_summary_project.return_value = False
                user_profile.reporter_id = "some_rep_id"
                submission_persister = SubmissionPersister(user, None, None, form_model, project)

                ignored_entries, saved_entries = submission_persister.save_submission(user_profile, valid_rows)

                self.assertEqual(saved_entries, [{"key":"value1"}, {"key":"value2"}])
                self.assertEqual(ignored_entries, [])

    def test_should_ignore_submissions_when_the_limit_has_exceeded(self):
        with patch("datawinners.project.submission.submission_import.Organization") as Organization:
            organization = MagicMock()
            Organization.objects.get.return_value= organization
            organization.has_exceeded_submission_limit.return_value = True
            user_profile = MagicMock()
            valid_rows = [{"key":"value1"}, {"key":"value2"}]
            with patch("datawinners.project.submission.submission_import.SurveyResponseService") as SurveyResponseService:
                service, project, user, form_model = Mock(), Mock(), Mock(), Mock()
                SurveyResponseService.return_value = service
                project.is_summary_project.return_value = True
                user_profile.reporter_id = "some_rep_id"
                submission_persister = SubmissionPersister(user, None, None, form_model, project)

                ignored_entries, saved_entries = submission_persister.save_submission(user_profile, valid_rows)

                self.assertEqual(ignored_entries, [{"key":"value1"}, {"key":"value2"}])
                self.assertEqual(saved_entries, [])

    def test_should_increment_web_count_for_each_successful_submission(self):
        with patch("datawinners.project.submission.submission_import.Organization") as Organization:
            organization = MagicMock()
            Organization.objects.get.return_value= organization
            organization.has_exceeded_submission_limit.return_value = False
            user_profile = MagicMock()
            valid_rows = [{"key":"value1"}, {"key":"value2"}]
            with patch("datawinners.project.submission.submission_import.SurveyResponseService") as SurveyResponseService:
                service, project, user, form_model = Mock(), Mock(), Mock(), Mock()
                SurveyResponseService.return_value = service
                project.is_summary_project.return_value = False
                user_profile.reporter_id = "some_rep_id"
                submission_persister = SubmissionPersister(user, None, None, form_model, project)

                submission_persister.save_submission(user_profile, valid_rows)

                self.assertEqual(organization.increment_message_count_for.call_count, 2)
                organization.increment_message_count_for.assert_called_with(incoming_web_count=1)


    def test_should_check_quotas_and_update_users_on_saving_submissions(self):
        with patch("datawinners.project.submission.submission_import.Organization") as Organization:
            organization = MagicMock()
            Organization.objects.get.return_value= organization
            organization.has_exceeded_submission_limit.return_value = False
            user_profile = MagicMock()
            valid_rows = [{}]
            with patch("datawinners.project.submission.submission_import.SurveyResponseService") as SurveyResponseService:
                service, project, user, form_model = Mock(), Mock(), Mock(), Mock()
                SurveyResponseService.return_value = service
                project.is_summary_project.return_value = False
                user_profile.reporter_id = "some_rep_id"
                submission_persister = SubmissionPersister(user, None, None, form_model, project)
                with patch("datawinners.project.submission.submission_import.check_quotas_and_update_users") as check_quotas_and_update_users:

                    submission_persister.save_submission(user_profile, valid_rows)

                    check_quotas_and_update_users.assert_called_with(organization)

    def test_should_save_survey_with_uploaded_entrys_report_id_for_summary_project_when_user_is_logged_in(self):
        with patch("datawinners.project.submission.submission_import.Organization") as Organization:
            organization = MagicMock()
            Organization.objects.get.return_value= organization
            organization.has_exceeded_submission_limit.return_value = False
            user_profile = MagicMock()
            expected_reporter_id = "rep_1"
            valid_row = {"eid": expected_reporter_id}
            valid_rows = [valid_row]
            with patch("datawinners.project.submission.submission_import.SurveyResponseService") as SurveyResponseService:
                service, project, user, form_model = Mock(), MagicMock(), Mock(), MagicMock()

                SurveyResponseService.return_value = service
                project.is_summary_project.return_value = True
                form_model.form_code = "form_code"
                submission_persister = SubmissionPersister(user, None, None, form_model, project)
                with patch("datawinners.project.submission.submission_import.is_org_user") as is_org_user:
                    with patch("datawinners.project.submission.submission_import.get_transport_info") as get_transport_info:
                        with patch("datawinners.project.submission.submission_import.get_feed_dictionary") as get_feed_dictionary:
                            transport_info = None
                            additional_feed_dictionary = None
                            get_feed_dictionary.return_value = additional_feed_dictionary
                            get_transport_info.return_value = transport_info
                            is_org_user.return_value = True

                            submission_persister.save_submission(user_profile, valid_rows)

                            service.save_survey.assert_called_with("form_code", valid_row, [],
                                                               transport_info, valid_row, expected_reporter_id,
                                                               additional_feed_dictionary)


    def test_should_save_survey_with_logged_in_datasenders_reporter_id(self):
        with patch("datawinners.project.submission.submission_import.Organization") as Organization:
            organization = MagicMock()
            Organization.objects.get.return_value= organization
            organization.has_exceeded_submission_limit.return_value = False
            user_profile = MagicMock()
            expected_reporter_id = "rep_1"
            user_profile.reporter_id = expected_reporter_id
            valid_row = {}
            valid_rows = [valid_row]
            with patch("datawinners.project.submission.submission_import.SurveyResponseService") as SurveyResponseService:
                service, project, user, form_model = Mock(), MagicMock(), Mock(), MagicMock()
                SurveyResponseService.return_value = service
                project.is_summary_project.return_value = False
                form_model.form_code = "form_code"
                submission_persister = SubmissionPersister(user, None, None, form_model, project)
                with patch("datawinners.project.submission.submission_import.is_org_user") as is_org_user:
                    with patch("datawinners.project.submission.submission_import.get_transport_info") as get_transport_info:
                        with patch("datawinners.project.submission.submission_import.get_feed_dictionary") as get_feed_dictionary:
                            transport_info = None
                            additional_feed_dictionary = None
                            get_feed_dictionary.return_value = additional_feed_dictionary
                            get_transport_info.return_value = transport_info
                            is_org_user.return_value = True

                            submission_persister.save_submission(user_profile, valid_rows)

                            service.save_survey.assert_called_with("form_code", valid_row, [],
                                                               transport_info, valid_row, expected_reporter_id,
                                                               additional_feed_dictionary)


from unittest import TestCase
import unittest
from django.contrib.auth.models import User
from mock import patch, Mock, MagicMock
from datawinners.project.models import Project
from datawinners.project.submission.submission_import import SubmissionPersister, SubmissionWorkbookValidator, SubmissionWorkbookMapper, ImportValidationError
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.field import TextField, UniqueIdField
from mangrove.form_model.form_model import FormModel


class TestSubmissionPersister(TestCase):
    def setUp(self):
        pass

    def test_should_save_submissions_when_the_limit_not_exceeded(self):
        submission_quota_service = MagicMock()
        submission_quota_service.has_exceeded_quota_and_notify_users.return_value = False
        user_profile = MagicMock()
        valid_rows = [{"key": "value1"}, {"key": "value2"}]
        with patch(
                "datawinners.project.submission.submission_import.SurveyResponseService") as SurveyResponseService:
            service, project, user, form_model = Mock(), Mock(), Mock(), Mock()
            SurveyResponseService.return_value = service
            project.is_summary_project.return_value = False
            user_profile.reporter_id = "some_rep_id"
            submission_persister = SubmissionPersister(user, None, None, form_model, project, submission_quota_service)

            ignored_entries, saved_entries = submission_persister.save_submissions(True, user_profile, valid_rows)

            self.assertEqual(saved_entries, [{"key": "value1"}, {"key": "value2"}])
            self.assertEqual(ignored_entries, [])

    def test_should_ignore_submissions_when_the_limit_has_exceeded(self):
        submission_quota_service = MagicMock()
        submission_quota_service.has_exceeded_quota_and_notify_users.return_value = True
        user_profile = MagicMock()
        valid_rows = [{"key": "value1"}, {"key": "value2"}]
        with patch(
                "datawinners.project.submission.submission_import.SurveyResponseService") as SurveyResponseService:
            service, project, user, form_model = Mock(), Mock(), Mock(), Mock()
            SurveyResponseService.return_value = service
            project.is_summary_project.return_value = True
            user_profile.reporter_id = "some_rep_id"
            submission_persister = SubmissionPersister(user, None, None, form_model, project, submission_quota_service)

            ignored_entries, saved_entries = submission_persister.save_submissions(True, user_profile, valid_rows)

            self.assertEqual(ignored_entries, [{"key": "value1"}, {"key": "value2"}])
            self.assertEqual(saved_entries, [])

    def test_should_increment_web_count_for_each_successful_submission(self):
        submission_quota_service = MagicMock()
        submission_quota_service.has_exceeded_quota_and_notify_users.return_value = False
        user_profile = MagicMock()
        valid_rows = [{"key": "value1"}, {"key": "value2"}]
        with patch(
                "datawinners.project.submission.submission_import.SurveyResponseService") as SurveyResponseService:
            service, project, user, form_model = Mock(), Mock(), Mock(), Mock()
            SurveyResponseService.return_value = service
            project.is_summary_project.return_value = False
            user_profile.reporter_id = "some_rep_id"
            submission_persister = SubmissionPersister(user, None, None, form_model, project, submission_quota_service)

            submission_persister.save_submissions(True, user_profile, valid_rows)

            self.assertEqual(submission_quota_service.increment_web_submission_count.call_count, 2)
            #organization.increment_message_count_for.assert_called_with(incoming_web_count=1)


    def test_should_check_quotas_and_update_users_on_saving_submissions(self):
        submission_quota_service = MagicMock()
        submission_quota_service.has_exceeded_quota_and_notify_users.return_value = False
        user_profile = MagicMock()
        valid_rows = [{}]
        with patch(
                "datawinners.project.submission.submission_import.SurveyResponseService") as SurveyResponseService:
            service, project, user, form_model = Mock(), Mock(), Mock(), Mock()
            SurveyResponseService.return_value = service
            project.is_summary_project.return_value = True
            user_profile.reporter_id = "some_rep_id"
            submission_persister = SubmissionPersister(user, None, None, form_model, project, submission_quota_service)

            submission_persister.save_submissions(True, user_profile, valid_rows)
            self.assertEqual(submission_quota_service.increment_web_submission_count.call_count, 1)

    def test_should_save_survey_with_uploaded_entrys_report_id_for_summary_project_when_user_is_logged_in(self):
        submission_quota_service = MagicMock()
        submission_quota_service.has_exceeded_quota_and_notify_users.return_value = False
        user_profile = MagicMock()
        expected_reporter_id = "rep_1"
        user_profile.reporter_id = expected_reporter_id
        valid_row = {"eid": expected_reporter_id}
        valid_rows = [valid_row]
        with patch("datawinners.project.submission.submission_import.SurveyResponseService") as SurveyResponseService:
            service, project, user, form_model = Mock(), MagicMock(), Mock(), MagicMock()

            SurveyResponseService.return_value = service
            project.is_summary_project.return_value = True
            form_model.form_code = "form_code"
            form_model.fields=[UniqueIdField(unique_id_type ='reporter', name="Q1", code="EID", label="What is the reporter ID?")]

            submission_persister = SubmissionPersister(user, None, None, form_model, project, submission_quota_service)
            with patch(
                    "datawinners.project.submission.submission_import.get_web_transport_info") as get_web_transport_info:
                with patch(
                        "datawinners.project.submission.submission_import.get_feed_dictionary") as get_feed_dictionary:
                    transport_info = None
                    additional_feed_dictionary = None
                    get_feed_dictionary.return_value = additional_feed_dictionary
                    get_web_transport_info.return_value = transport_info

                    submission_persister.save_submissions(True, user_profile, valid_rows)

                    service.save_survey.assert_called_with("form_code", valid_row, [],
                                                           transport_info, valid_row, expected_reporter_id,
                                                           additional_feed_dictionary)


    def test_should_save_survey_with_logged_in_datasenders_reporter_id(self):
        submission_quota_service = MagicMock()
        submission_quota_service.has_exceeded_quota_and_notify_users.return_value = False
        user_profile = MagicMock()
        expected_reporter_id = "rep_1"
        user_profile.reporter_id = expected_reporter_id
        valid_row = {}
        valid_rows = [valid_row]
        with patch(
                "datawinners.project.submission.submission_import.SurveyResponseService") as SurveyResponseService:
            service, project, user, form_model = Mock(), MagicMock(), Mock(), MagicMock()
            SurveyResponseService.return_value = service
            project.is_summary_project.return_value = True
            form_model.form_code = "form_code"
            submission_persister = SubmissionPersister(user, None, None, form_model, project, submission_quota_service)
            with patch(
                    "datawinners.project.submission.submission_import.get_web_transport_info") as get_web_transport_info:
                with patch(
                        "datawinners.project.submission.submission_import.get_feed_dictionary") as get_feed_dictionary:
                    transport_info = None
                    additional_feed_dictionary = None
                    get_feed_dictionary.return_value = additional_feed_dictionary
                    get_web_transport_info.return_value = transport_info

                    submission_persister.save_submissions(False, user_profile, valid_rows)

                    service.save_survey.assert_called_with("form_code", valid_row, [],
                                                           transport_info, valid_row, expected_reporter_id,
                                                           additional_feed_dictionary)


class SubmissionParserTest(TestCase):
    def setUp(self):
        self.data = [[
                    "What is the reporting period for the activity?\n\n Answer must be a date in the following format: day.month.year\n\n Example: 25.12.2011"],
                ["12.12.2012"],
                ["11.11.2012"],
                ["12.10.2012"],
        ]
        self.user = Mock(User)
        self.dbm = Mock(spec=DatabaseManager)
        fields = \
            [UniqueIdField('clinic',name="Q1", code="EID", label="What is the reporter ID?"),
             TextField(name="Q2", code="DATE", label="What is the reporting period for the activity?")]
        self.form_model = FormModel(self.dbm, "abc", "abc", form_code="cli001", fields=fields,
                               type="survey")
        self.project = Mock(Project)

    def add_datasender_col(self):
        self.data[0].insert(0, "What is the reporter ID?")
        for row in self.data[1:]: row.insert(0, "ds1")

    def test_should_process_submission_import_worksheet_for_datasender(self):
        expected_ans_dict = [{'DATE': '12.12.2012'}, {'DATE': '11.11.2012'}, {'DATE': '12.10.2012'}]
        self.assertEquals(expected_ans_dict, SubmissionWorkbookMapper(self.data, self.form_model).process());

    def test_process_submission_import_worksheet_test_for_datasender(self):
        self.add_datasender_col()
        ans_dict = SubmissionWorkbookMapper(self.data, self.form_model).process()
        try:
            SubmissionWorkbookValidator(self.form_model).validate(ans_dict)
        except ImportValidationError as e:
            self.assertEquals("The columns you are importing do not match the current Questionnaire. Please download the latest template for importing.", e.message)

    def test_submission_import_worksheet_should_have_datasender_id(self):
        self.add_datasender_col()
        ans_dict = SubmissionWorkbookMapper(self.data, self.form_model).process()
        self.assertEquals(None, SubmissionWorkbookValidator(self.form_model).validate(ans_dict))

    def test_validate_template_for_datasender(self):
        data = SubmissionWorkbookMapper(self.data, self.form_model).process()
        try:
            SubmissionWorkbookValidator(self.form_model).validate(data)
        except ImportValidationError as e:
            self.assertEquals("The columns you are importing do not match the current Questionnaire. Please download the latest template for importing.", e.message)


    def test_should_handle_questions_with_similar_label(self):
        self.data = [[
                    "What is the reporting period for the activity?\n\n Answer must be a date in the following format: day.month.year\n\n Example: 25.12.2011",
                    "Name",
                    "Name 1"],

                ["12.12.2012", "name11", "name12"],
                ["11.11.2012", "name21", "name22"],
                ["12.10.2012", "name31", "name32"]
        ]
        field = TextField(name="Q3", code="NAME", label="Name")
        self.form_model.add_field(field)
        field = TextField(name="Q4", code="NAME1", label="Name 1")
        self.form_model.add_field(field)
        expected_ans_dict = [{'DATE': '12.12.2012', 'NAME': 'name11', 'NAME1': 'name12'},
                             {'DATE': '11.11.2012', 'NAME': 'name21', 'NAME1': 'name22'},
                             {'DATE': '12.10.2012', 'NAME': 'name31', 'NAME1': 'name32'}]

        self.assertEquals(expected_ans_dict, SubmissionWorkbookMapper(self.data, self.form_model).process());

if __name__ == '__main__':
    unittest.main()
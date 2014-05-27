from unittest import TestCase
from mock import patch, Mock, MagicMock
from datawinners.messageprovider.handlers import success_questionnaire_submission_handler
from datawinners.project.models import Project
from mangrove.form_model.form_model import FormModel


class TestSuccessfulSubmissionReplyMessage(TestCase):
    @patch.object(Project, 'from_form_model')
    def test_should_return_message_with_name_and_answer_list_substituted_when_message_length_is_less_than_or_equal_160_chars(
            self, ProjectMock):
        dbm = Mock()
        with patch(
                'datawinners.messageprovider.customized_message.get_form_model_by_code') as get_form_model_by_code_mock:
            get_form_model_by_code_mock.return_value = MagicMock(spec=FormModel)

            project_mock = MagicMock(spec=Project)
            ProjectMock.from_form_model.return_value = project_mock
            project_mock.language = "en"

            with patch(
                    'datawinners.messageprovider.customized_message.customized_message_details') as customized_message_details_mock:
                customized_message_details_mock.return_value = [
                    {'message': "Thank you {Name of Data Sender}. We received your SMS: {List of Answers}",
                     'code': 'reply_success_submission'}]

                actual_message = success_questionnaire_submission_handler(dbm, 123, 'DS Name', "a1; a2")

        self.assertEqual(actual_message, "Thank you DS Name. We received your SMS: a1; a2")

    @patch.object(Project, 'from_form_model')
    def test_should_return_message_with_only_datasender_name_when_customized_message_including_answer_list_is_greater_than_160_chars(
            self, ProjectMock):
        dbm = Mock()
        answer_list = "a1;a2" * 100

        with patch(
                'datawinners.messageprovider.customized_message.get_form_model_by_code') as get_form_model_by_code_mock:
            get_form_model_by_code_mock.return_value = MagicMock(spec=FormModel)

            project_mock = MagicMock(spec=Project)
            ProjectMock.from_form_model.return_value = project_mock
            project_mock.language = "en"

            with patch(
                    'datawinners.messageprovider.customized_message.customized_message_details') as customized_message_details_mock:
                customized_message_details_mock.return_value = [
                    {'message': "Thank you {Name of Data Sender}. We received your SMS: {List of Answers}",
                     'code': 'reply_success_submission'}]

                actual_message = success_questionnaire_submission_handler(dbm, 123, 'DS Name', answer_list)

        self.assertEqual(actual_message, "Thank you DS Name. We received your SMS.")



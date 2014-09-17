import unittest
from datawinners.project.wizard_view import update_associated_submissions, update_submissions_for_form_code_change, remove_deleted_questions_from_submissions
from mangrove.datastore.database import DatabaseManager
from mock import patch, Mock, MagicMock
from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import FormModel
from mangrove.transport.contract.survey_response import SurveyResponse


class TestUpdateAssociatedSubmission(unittest.TestCase):
    def test_should_update_the_associated_submission_when_question_code_is_updated(self):
        update_dict = {"database_name": "database_name", "old_form_code": "old_form_code",
                       "new_form_code": "new_form_code", "new_revision": "new_revision"}

        with patch("datawinners.project.wizard_view.get_db_manager") as get_db_manager:
            managerMock = Mock(spec=DatabaseManager)
            get_db_manager.return_value = managerMock
            managerMock._save_documents.return_value = []
            with patch(
                    "datawinners.project.wizard_view.survey_responses_by_form_code") as survey_responses_by_form_code:
                mock_document1 = SurveyResponseDocument()
                mock_document2 = SurveyResponseDocument()
                survey_responses_mock = [(SurveyResponse.new_from_doc(dbm=None, doc=mock_document1)),
                                         (SurveyResponse.new_from_doc(dbm=None, doc=mock_document2))]
                survey_responses_by_form_code.return_value = survey_responses_mock

                update_submissions_for_form_code_change(managerMock, 'new_form_code', 'old_form_code')
                managerMock._save_documents.assert_called_with([mock_document1, mock_document2])
                self.assertEquals(mock_document1.form_model_id, "new_form_code")
                self.assertEquals(mock_document2.form_model_id, "new_form_code")

    def test_should_update_submissions_for_form_field_change(self):
        dbm = Mock(spec=DatabaseManager)
        form_code = 'code'
        deleted_question_codes = ['field_code']
        with patch("datawinners.project.wizard_view.survey_responses_by_form_code") as survey_responses_by_form_code:
            mock_document1 = Mock(spec=SurveyResponseDocument,
                                  values={'field_code': 'answer1', 'another_code': 'answer2'})
            mock_document2 = Mock(spec=SurveyResponseDocument,
                                  values={'field_code': 'answer3', 'another_code': 'answer4'})
            survey_response1 = MagicMock(spec=SurveyResponse)
            survey_response1._doc = mock_document1
            survey_response2 = MagicMock(spec=SurveyResponse)
            survey_response2._doc = mock_document2
            survey_responses_mock = [survey_response1,survey_response2]
            survey_responses_by_form_code.return_value = survey_responses_mock

            remove_deleted_questions_from_submissions(dbm, form_code, deleted_question_codes)

            survey_response1.save.assert_called()
            survey_response2.save.assert_called()
            self.assertEquals(mock_document1.values, {'another_code': 'answer2'})
            self.assertEquals(mock_document2.values, {'another_code': 'answer4'})

    def test_should_not_update_submissions_no_field_got_deleted(self):
        dbm = Mock(spec=DatabaseManager)
        form_code = 'code'
        deleted_question_codes = []
        with patch("datawinners.project.wizard_view.survey_responses_by_form_code") as survey_responses_by_form_code:
            mock_document1 = SurveyResponseDocument(values={'field_code': 'answer1', 'another_code': 'answer2'})
            mock_document2 = SurveyResponseDocument(values={'field_code': 'answer3', 'another_code': 'answer4'})
            survey_responses_mock = [(SurveyResponse.new_from_doc(dbm=None, doc=mock_document1)),
                                     (SurveyResponse.new_from_doc(dbm=None, doc=mock_document2))]
            survey_responses_by_form_code.return_value = survey_responses_mock

            remove_deleted_questions_from_submissions(dbm, form_code, deleted_question_codes)

            self.assertEquals(mock_document1.values, {'field_code': 'answer1', 'another_code': 'answer2'})
            self.assertEquals(mock_document2.values, {'field_code': 'answer3', 'another_code': 'answer4'})



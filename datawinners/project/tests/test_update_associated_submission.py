import unittest
from datawinners.project.wizard_view import update_associated_submissions, update_submissions_for_form_code_change, update_submissions_for_form_field_change
from mangrove.datastore.database import DatabaseManager
from mock import patch, Mock, MagicMock
from mangrove.datastore.datadict import DataDictType
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
                self.assertEquals(mock_document1.form_code, "new_form_code")
                self.assertEquals(mock_document2.form_code, "new_form_code")

    def test_should_update_submissions_for_form_field_change(self):
        dbm = Mock(spec=DatabaseManager)
        field = TextField(name='name', label='question label 1', code='field_code', ddtype=Mock(spec=DataDictType))
        old_form_model = MagicMock()
        old_form_model.fields = [field]
        old_form_model._doc.form_code = 'form_code'
        new_form_model = Mock(spec=FormModel)
        changed_questions = {'deleted': ['question label 1']}
        with patch("datawinners.project.wizard_view.survey_responses_by_form_code") as survey_responses_by_form_code:
            mock_document1 = SurveyResponseDocument(values={'field_code': 'answer1', 'another_code': 'answer2'})
            mock_document2 = SurveyResponseDocument(values={'field_code': 'answer3', 'another_code': 'answer4'})
            survey_responses_mock = [(SurveyResponse.new_from_doc(dbm=None, doc=mock_document1)),
                                     (SurveyResponse.new_from_doc(dbm=None, doc=mock_document2))]
            survey_responses_by_form_code.return_value = survey_responses_mock

            update_submissions_for_form_field_change(dbm, new_form_model, old_form_model, changed_questions)

            dbm._save_documents.assert_called_with([mock_document1, mock_document2])
            self.assertEquals(mock_document1.values, {'another_code': 'answer2'})
            self.assertEquals(mock_document2.values, {'another_code': 'answer4'})

    def test_should_not_update_submissions_no_field_got_deleted(self):
        dbm = Mock(spec=DatabaseManager)
        field = TextField(name='name', label='question label 1', code='field_code', ddtype=Mock(spec=DataDictType))
        old_form_model = MagicMock()
        old_form_model.fields = [field]
        old_form_model._doc.form_code = 'form_code'
        new_form_model = Mock(spec=FormModel)
        changed_questions = {'added': ['question label 1']}
        with patch("datawinners.project.wizard_view.survey_responses_by_form_code") as survey_responses_by_form_code:
            mock_document1 = SurveyResponseDocument(values={'field_code': 'answer1', 'another_code': 'answer2'})
            mock_document2 = SurveyResponseDocument(values={'field_code': 'answer3', 'another_code': 'answer4'})
            survey_responses_mock = [(SurveyResponse.new_from_doc(dbm=None, doc=mock_document1)),
                                     (SurveyResponse.new_from_doc(dbm=None, doc=mock_document2))]
            survey_responses_by_form_code.return_value = survey_responses_mock

            update_submissions_for_form_field_change(dbm, new_form_model, old_form_model, changed_questions)

            self.assertEquals(mock_document1.values, {'field_code': 'answer1','another_code': 'answer2'})
            self.assertEquals(mock_document2.values, {'field_code': 'answer3','another_code': 'answer4'})



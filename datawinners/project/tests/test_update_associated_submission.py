import unittest
from datawinners.project.wizard_view import update_associated_submissions
from mangrove.datastore.database import DatabaseManager
from mock import patch, Mock
from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.transport.contract.survey_response import SurveyResponse


class TestUpdateAssociatedSubmission(unittest.TestCase):

    def test_should_update_the_associated_submission_when_question_code_is_updated(self):

        update_dict = {"database_name": "database_name", "old_form_code": "old_form_code",
                         "new_form_code": "new_form_code", "new_revision":"new_revision"}

        with patch("datawinners.project.wizard_view.get_db_manager") as get_db_manager:
            managerMock = Mock(spec=DatabaseManager)
            get_db_manager.return_value = managerMock
            managerMock._save_documents.return_value = []
            with patch("datawinners.project.wizard_view.survey_responses_by_form_code") as survey_responses_by_form_code:
                mock_document1 = SurveyResponseDocument()
                mock_document2 = SurveyResponseDocument()
                survey_responses_mock = [(SurveyResponse.new_from_doc(dbm=None, doc=mock_document1)),
                                         (SurveyResponse.new_from_doc(dbm=None, doc=mock_document2))]
                survey_responses_by_form_code.return_value = survey_responses_mock

                update_associated_submissions(update_dict)
                managerMock._save_documents.assert_called_with([mock_document1,mock_document2])
                self.assertEquals(mock_document1.form_code,"new_form_code")
                self.assertEquals(mock_document2.form_code,"new_form_code")
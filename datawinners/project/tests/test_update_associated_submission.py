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
                survey_responses_mock = [(SurveyResponse.new_from_doc(dbm=None, doc=SurveyResponseDocument())),
                                         (SurveyResponse.new_from_doc(dbm=None, doc=SurveyResponseDocument()))]
                survey_responses_by_form_code.return_value = survey_responses_mock

                update_associated_submissions(update_dict)

                expected_docs = [SurveyResponseDocument(form_code='new_form_code', form_model_revision='new_revision'), SurveyResponseDocument(form_code='new_form_code', form_model_revision='new_revision')]
                managerMock._save_documents.called_with(expected_docs)

from collections import OrderedDict
from unittest import TestCase, SkipTest
from mock import Mock, patch, MagicMock, PropertyMock
from datawinners.project.submission.validator import SubmissionWorkbookRowValidator
from mangrove.form_model.form_model import FormModel


class TestImportSubmissionValidator(TestCase):

    def test_should_return_valid_rows(self):
        form_model_mock = MagicMock(spec=FormModel)
        form_model_mock.validate_submission.return_value = ([],[])
        validator = SubmissionWorkbookRowValidator(Mock(), form_model_mock)
        parsed_rows = [OrderedDict(), OrderedDict()]

        valid_rows, invalid_rows = validator.validate_rows(parsed_rows)

        self.assertEqual(len(valid_rows), 2)
        self.assertEqual(len(invalid_rows), 0)

    def test_should_return_invalid_rows(self):
        form_model_mock, project_mock = MagicMock(), MagicMock()
        form_model_mock.form_fields = []

        entity_question = PropertyMock(return_value=None)
        type(form_model_mock).entity_question = entity_question
        form_model_mock.validate_submission.return_value = ([],{"error":"error_msg"})
        with patch("datawinners.project.submission.validator.translate_errors") as translate_errors:
            translate_errors.return_value = ["error_msg"]
            validator = SubmissionWorkbookRowValidator(Mock(), form_model_mock)
            parsed_rows = [OrderedDict(), OrderedDict()]

            valid_rows, invalid_rows = validator.validate_rows(parsed_rows)

            self.assertEqual(len(valid_rows), 0)
            self.assertEqual(len(invalid_rows), 2)
            self.assertEquals(invalid_rows[0]['errors'],['error_msg'])
            self.assertEquals(invalid_rows[1]['errors'],['error_msg'])

    def test_should_validate_datasenders(self):
        form_model_mock, project_mock = MagicMock(), MagicMock()
        form_model_mock.form_fields = []
        form_model_mock.data_senders = ['rep2']

        entity_question = PropertyMock(return_value=None)
        type(form_model_mock).entity_question = entity_question
        form_model_mock.validate_submission.return_value = ([],{})
        #with patch("datawinners.project.submission.validator.translate_errors") as translate_errors:
        #    translate_errors.return_value = ["error_msg"]
        validator = SubmissionWorkbookRowValidator(Mock(), form_model_mock)
        parsed_rows = [OrderedDict({'dsid':'rep3'}), OrderedDict({'user_dsid':'rep4', 'dsid': 'rep4'})]

        valid_rows, invalid_rows = validator.validate_rows(parsed_rows)

        self.assertEqual(len(valid_rows), 0)
        self.assertEqual(len(invalid_rows), 2)
        self.assertEquals(invalid_rows[0]['errors'], [u'The Data Sender you are submitting on behalf of cannot submit to this Questionnaire. Add the Data Sender to the Questionnaire.'])
        self.assertEquals(invalid_rows[1]['errors'], [u'You are not authorized to submit to this Questionnaire. Add yourself as a Data Sender to the Questionnaire.'])


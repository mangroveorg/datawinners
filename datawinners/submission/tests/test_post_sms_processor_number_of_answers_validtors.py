import unittest
from mangrove.contrib.registration import GLOBAL_REGISTRATION_FORM_CODE
from mangrove.errors.MangroveException import SMSParserWrongNumberOfAnswersException
from mangrove.form_model.form_model import FormModel, EntityFormModel
from mock import patch, Mock
from datawinners.messageprovider.messages import get_wrong_number_of_answer_error_message
from datawinners.submission.submission_utils import PostSMSProcessorNumberOfAnswersValidators

class TestPostSMSProcessorNumberOfAnswersValidators(unittest.TestCase):
    def setUp(self):
        self.language = 'fr'
        self.patcher = patch('datawinners.submission.submission_utils.get_form_model_by_code')
        self.form_model_patch = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_for_activity_report_question_should_send_error_for_data_submission_if_number_of_answers_are_not_equal_to_number_of_questions(self):
        # there won't be any answers for entity question
        self.form_model_patch.return_value = self._get_form_model_mock(is_registration_form=False, fields=[1, 2, 3])

        processor = PostSMSProcessorNumberOfAnswersValidators(dbm=None, request={})
        self.assertRaises(SMSParserWrongNumberOfAnswersException, processor.process, "form_code", {'q1': 'ans', })
        #self.assertEqual(False, response.success)
        #self.assertEqual(get_wrong_number_of_answer_error_message(), response.errors)

    def test_should_not_send_error_for_data_submission_if_number_of_answers_are_correct(self):
        self.form_model_patch.return_value = self._get_form_model_mock(is_registration_form=False, fields=[1, 2])
        processor = PostSMSProcessorNumberOfAnswersValidators(dbm=None, request={})
        response = processor.process("form_code", {'q1': 'ans', 'q2': 'ans2'})
        self.assertEqual(None, response)

    def test_for_registration_should_not_send_error_if_number_of_answers_incorrect_when_short_code_question_is_present(
            self):
        self.form_model_patch.return_value = self._get_form_model_mock(is_registration_form=True, fields=[1, 2, 3])
        processor = PostSMSProcessorNumberOfAnswersValidators(dbm=None, request={})
        response = processor.process("form_code", {'q1': 'ans', 'q2': 'ans2'})
        self.assertEqual(None, response)

    def test_for_registration_should_send_error_if_number_of_answers_incorrect_when_subject_question_is_present(self):
        self.form_model_patch.return_value = self._get_form_model_mock(is_registration_form=True, fields=[1, 2, 3, 4])
        processor = PostSMSProcessorNumberOfAnswersValidators(dbm=None, request={})
        self.assertRaises(  SMSParserWrongNumberOfAnswersException, processor.process,"form_code", {'q1': 'ans', 'q2': 'ans2'})
        self.assertRaisesRegexp(SMSParserWrongNumberOfAnswersException,"%d")
        #self.assertEqual(False, response.success)
        #self.assertEqual(get_wrong_number_of_answer_error_message(), response.errors)

    def test_for_registration_should_send_error_if_number_of_answers_incorrect_when_subject_question_is_not_present(
            self):
        self.form_model_patch.return_value = self._get_form_model_mock(is_registration_form=True, fields=[1, 2, 3])
        processor = PostSMSProcessorNumberOfAnswersValidators(dbm=None, request={})
        self.assertRaises(SMSParserWrongNumberOfAnswersException, processor.process ,"form_code", {'q1': 'ans'})

    def test_for_registration_should_not_send_error_if_number_of_answers_correct_when_subject_question_is_not_present(
            self):
        self.form_model_patch.return_value = self._get_form_model_mock(is_registration_form=True, fields=[1, 2])
        processor = PostSMSProcessorNumberOfAnswersValidators(dbm=None, request={})
        response = processor.process("form_code", {'q1': 'ans', 'q2': 'ans2'})
        self.assertEqual(None, response)

    def test_for_registration_should_not_send_error_for_global_registration_form(self):
        self.form_model_patch.return_value = self._get_form_model_mock(is_registration_form=True, fields=[1, 2])
        processor = PostSMSProcessorNumberOfAnswersValidators(dbm=None, request={})
        response = processor.process(GLOBAL_REGISTRATION_FORM_CODE, {'q1': 'ans', 'q2': 'ans2'})
        self.assertEqual(None, response)


    def _get_form_model_mock(self, is_registration_form, fields, entity_question =None):
        form_model_mock = Mock(spec=EntityFormModel) if is_registration_form else Mock(spec=FormModel)
        form_model_mock.is_entity_registration_form.return_value = is_registration_form
        form_model_mock.fields = fields
        return form_model_mock

    def test_for_activity_report_question_should_send_error_for_data_submission_with_extra_answers(self):
        self.form_model_patch.return_value = self._get_form_model_mock(is_registration_form=False, fields=[1, 2, 3])

        processor = PostSMSProcessorNumberOfAnswersValidators(dbm=None, request={})
        response = processor.process("form_code", {'q1': 'ans', 'q2': 'ans2'}, ["tsara", "bien", "cool"])
        self.assertEqual(False, response.success)
        self.assertEqual(get_wrong_number_of_answer_error_message(), response.errors)
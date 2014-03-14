from django.utils import translation
from mangrove.contrib.registration import GLOBAL_REGISTRATION_FORM_CODE
from mangrove.errors.MangroveException import SMSParserWrongNumberOfAnswersException
from mangrove.form_model.form_model import get_form_model_by_code, FORM_CODE
from mangrove.transport.contract.response import Response
from datawinners.messageprovider.messages import get_wrong_number_of_answer_error_message

class PostSMSProcessorLanguageActivator(object):
    def __init__(self, dbm, request):
        self.dbm = dbm
        self.request = request

    def process(self, form_code, submission_values):
        self.request[FORM_CODE] = form_code
        form_model = get_form_model_by_code(self.dbm, form_code)
        translation.activate(form_model.activeLanguages[0])


class PostSMSProcessorNumberOfAnswersValidators(object):
    def __init__(self, dbm, request):
        self.dbm = dbm
        self.request = request

    def process(self, form_code, submission_values, extra_data=[]):
        if len(extra_data):
            return self._get_wrong_number_of_question_response()
        form_model = get_form_model_by_code(self.dbm, form_code)

        processor_func = self._get_handlers(form_model)
        response = processor_func(form_model, submission_values)
        if response and not response.success:
            raise SMSParserWrongNumberOfAnswersException(form_code)
        return response



    def _get_handlers(self,form_model):
        if form_model.is_entity_registration_form():
            return self._process_registration_request
        else:
            return self._process_data_submission_request

    def _get_wrong_number_of_question_response(self):
        response = Response(reporters=[], survey_response_id=None)
        response.success = False
        response.errors = get_wrong_number_of_answer_error_message()
        return response

    def _process_registration_when_entity_question_is_present(self, form_model, submission_values):
        # the answer to short code question may or may not present
        if (self._correct_number_of_questions_with_short_code_present(form_model, submission_values)) or (
        self._correct_number_of_questions_with_short_code_absent(form_model, submission_values)):
            return None
        return self._get_wrong_number_of_question_response()

    def _correct_number_of_questions_with_short_code_present(self, form_model, submission_values):
        return len(form_model.fields) == len(submission_values.keys())

    def _correct_number_of_questions_with_short_code_absent(self, form_model, submission_values):
        if form_model.is_entity_registration_form():
            return len(form_model.fields) == len(submission_values.keys()) + 1
        return False

    def _process_registration_when_entity_question_is_absent(self, form_model, submission_values):
        if len(form_model.fields) != len(submission_values.keys()):
            return self._get_wrong_number_of_question_response()

    def _process_registration_request(self, form_model, submission_values):
        if form_model.form_code == GLOBAL_REGISTRATION_FORM_CODE:
            return None

        if form_model.entity_question is not None:
            return self._process_registration_when_entity_question_is_present(form_model, submission_values)
        else:
            return self._process_registration_when_entity_question_is_absent(form_model, submission_values)

    def _process_data_submission_request(self, form_model, submission_values):
        return self._process_registration_when_entity_question_is_present(form_model,submission_values)



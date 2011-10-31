from collections import OrderedDict
from mangrove.errors.MangroveException import SMSParserWrongNumberOfAnswersException, SMSParserInvalidFormatException, MultipleSubmissionsForSameCodeException
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.player.parser import SMSParser
from mangrove.utils.types import is_empty, is_string

class OrderSMSParser(SMSParser):
    SEPARATOR_FOR_NO_FIELD_ID = u" "

    def __init__(self, dbm):
        self.dbm = dbm

    def _parse_tokens(self, tokens, question_codes):
        submission = OrderedDict()

        if len(tokens) != len(question_codes):
            raise SMSParserWrongNumberOfAnswersException()

        for token_index in range(len(tokens)):
            token = tokens[token_index]
            if is_empty(token): continue
            submission[question_codes[token_index]] = token
        return submission

    def parse(self, message):
        assert is_string(message)
        try:
            form_code, tokens = self.form_code(message)
            form_code = self._pop_form_code(tokens)
            question_codes = self._get_question_codes_from_couchdb(form_code)
            submission = self._parse_tokens(tokens, question_codes)
        except SMSParserInvalidFormatException as ex:
            raise SMSParserInvalidFormatException(ex.data)
        return form_code, submission

    def form_code(self, message):
        message = self._clean(message)
        self._validate_format(self.MESSAGE_PREFIX_NO_FIELD_ID,message)
        tokens = message.split()
        form_code = self._pop_form_code(tokens)
        return form_code, tokens

    def _get_question_codes_from_couchdb(self,form_code):
        questionnaire_form = get_form_model_by_code(self.dbm, form_code)
        question_codes = []
        for aField in questionnaire_form.fields:
            question_codes.append(aField.code)
        return question_codes

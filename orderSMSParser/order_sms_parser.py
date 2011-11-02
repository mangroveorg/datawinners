from collections import OrderedDict
from mangrove.errors.MangroveException import SMSParserWrongNumberOfAnswersException, SMSParserInvalidFormatException, MultipleSubmissionsForSameCodeException
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.player.parser import SMSParser
from mangrove.utils.types import is_empty, is_string

class OrderSMSParser(SMSParser):
    MESSAGE_PREFIX_FOR_ORDERED_SMS = ur'^(\w+)\s+(\w+)'

    def __init__(self, dbm):
        self.dbm = dbm

    def _parse_ordered_tokens(self, tokens, question_codes):
        submission = OrderedDict()

        if len(tokens) != len(question_codes):
            print tokens
            print question_codes
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
            question_codes = self._get_question_codes_from_couchdb(form_code)
            submission = self._parse_ordered_tokens(tokens, question_codes)
        except SMSParserInvalidFormatException as ex:
            raise SMSParserInvalidFormatException(ex.data)
        return form_code, submission

    def form_code(self, message):
        message = self._clean(message)
        self._validate_format(self.MESSAGE_PREFIX_FOR_ORDERED_SMS,message)
        tokens = message.split()
        form_code = self._pop_form_code(tokens)
        return form_code, tokens

    def _get_question_codes_from_couchdb(self,form_code):
        questionnaire_form = get_form_model_by_code(self.dbm, form_code)
        question_codes = []
        form_fields = questionnaire_form.fields
        print questionnaire_form.entity_type[0]
        print questionnaire_form.entity_type[0] == 'reporter'
        if questionnaire_form.entity_type[0] == 'reporter':
            form_fields.remove(form_fields[0])
        for aField in form_fields:
            question_codes.append(aField.code)
        return question_codes



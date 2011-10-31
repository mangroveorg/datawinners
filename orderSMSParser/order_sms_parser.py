from collections import OrderedDict
from mangrove.errors.MangroveException import SMSParserWrongNumberOfAnswersException, SMSParserInvalidFormatException, MultipleSubmissionsForSameCodeException
from mangrove.transport.player.parser import SMSParser
from mangrove.utils.types import is_empty, is_string

class OrderSMSParser(SMSParser):
    SEPARATOR_FOR_NO_FIELD_ID = u" "

    def _parse_tokens(self, tokens, question_codes):
        submission = OrderedDict()

        if len(tokens) != len(question_codes):
            raise SMSParserWrongNumberOfAnswersException()

        for token_index in range(len(tokens)):
            token = tokens[token_index]
            if is_empty(token): continue
            submission[question_codes[token_index]] = token
        return submission

    def parse_ordered_sms(self, message, question_codes):
        assert is_string(message)
        return self._parse_ordered_sms(message, question_codes)

    def _parse_ordered_sms(self, message, question_codes):
        try:
            message = self._clean(message)
            self._validate_format(self.MESSAGE_PREFIX_NO_FIELD_ID, message)
            tokens = message.split()
            form_code = self._pop_form_code(tokens)
            submission = self._parse_tokens(tokens, question_codes)

        except SMSParserInvalidFormatException as ex:
            raise SMSParserInvalidFormatException(ex.data)

        return form_code, submission
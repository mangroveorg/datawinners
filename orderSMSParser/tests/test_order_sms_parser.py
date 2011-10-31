import unittest
from django.conf import settings
from datawinners.orderSMSParser.order_sms_parser import OrderSMSParser
from mangrove.errors.MangroveException import SMSParserWrongNumberOfAnswersException, SMSParserInvalidFormatException

class TestOrderSMSParser(unittest.TestCase):
    def setUp(self):
        self.sms_parser = OrderSMSParser()
        settings.USE_ORDERED_SMS_PARSER = True

    def test_should_return_all_answers(self):
        message = "questionnaire_code question1_answer question2_answer question3_answer"
        question_code = ['q1', 'q2', 'q3']
        values = self.sms_parser.parse_ordered_sms(message, question_code)
        question_code_and_answers = {"q1": "question1_answer", "q2": "question2_answer", "q3": "question3_answer"}
        expected = ("questionnaire_code", question_code_and_answers)
        self.assertEqual(expected, values)

    def test_should_accept_only_strings_parsing_without_field(self):
        with self.assertRaises(AssertionError):
            self.sms_parser.parse(10)
        with self.assertRaises(AssertionError):
            self.sms_parser.parse(None)

    def test_num_of_answers_not_the_same_as_num_of_questions(self):
        message = "questionnaire_code question1_answer question2_answer"
        question_code = ['q1', 'q2', 'q3']
        self.assertRaises(SMSParserWrongNumberOfAnswersException, self.sms_parser.parse_ordered_sms,
                          message, question_code)

    def test_invalid_format_message(self):
        message = "questionnaire_code .q1 question1_answer .q2 question2_answer .q3 question3_answer"
        question_code = ['q1', 'q2', 'q3']
        self.assertRaises(SMSParserInvalidFormatException, self.sms_parser.parse_ordered_sms,
                          message, question_code)
    def tearDown(self):
        settings.USE_ORDERED_SMS_PARSER = False
  
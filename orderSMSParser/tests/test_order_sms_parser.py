import unittest
from django.conf import settings
from datawinners.orderSMSParser.order_sms_parser import OrderSMSParser

class TestOrderSMSParser(unittest.TestCase):

    def setUp(self):
        self.sms_parser = OrderSMSParser()
        settings.USE_ORDERED_SMS_PARSER = True

    def test_should_return_all_answers_in_lower_case_ordered_format(self):
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

    def tearDown(self):
        settings.USE_ORDERED_SMS_PARSER = False
  
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from mangrove.datastore.database import DatabaseManager
from django.utils.translation import get_language
from mangrove.form_model.form_model import FormModel
from mangrove.errors.MangroveException import NumberNotRegisteredException, DataObjectNotFound, SMSParserWrongNumberOfAnswersException
from mock import Mock, patch
from messageprovider.exception_handler import handle
from messageprovider.message_handler import get_exception_message_for
from messageprovider.messages import SMS, exception_messages
from submission.models import DatawinnerLog

class TestExceptionHandler(unittest.TestCase):

    def setUp(self):
        self.datawinner_log_mock = Mock(spec=DatawinnerLog)
        self.datawinner_log_mock.error = ''

        self.request = dict(datawinner_log=self.datawinner_log_mock)

    def test_should_handle_NumberNotRegisteredException(self):
        exception = NumberNotRegisteredException('1234312')

        expected_message = get_exception_message_for(exception, SMS)
        response = handle(exception, self.request)

        self.assertEqual(expected_message, response)
        self.assertEqual(expected_message, self.request['datawinner_log'].error)

    def test_should_handle_DataObjectNotFoundException(self):
        exception = DataObjectNotFound('test_entity','id','123')
        exception_message_dict = exception_messages[type(exception)]
        expected_message = exception_message_dict.get(SMS) % ('test_entity','123','test_entity')
        response = handle(exception, self.request)
        self.assertEqual(expected_message, response)

    def test_should_handle_SMSParserWrongNumberOfAnswersException(self):
        exception = SMSParserWrongNumberOfAnswersException('test_code')

        form_model_mock = Mock(spec=FormModel)
        patcher = patch('messageprovider.handlers.get_form_model_by_code')
        get_form_model_mock = patcher.start()
        get_form_model_mock.return_value = form_model_mock
        form_model_mock.activeLanguages = ['en']
        self.request['dbm'] = Mock(spec=DatabaseManager)
        expected_message = get_exception_message_for(exception, channel=SMS)

        response = handle(exception, self.request)

        self.assertEqual(expected_message, response)
        self.assertEqual('en', get_language())
        patcher.stop()
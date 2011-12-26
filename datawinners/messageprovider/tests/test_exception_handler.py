# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from mangrove.datastore.database import DatabaseManager
from django.utils.translation import get_language
from mangrove.form_model.form_model import FormModel, FORM_CODE
from mangrove.errors.MangroveException import NumberNotRegisteredException, DataObjectNotFound, SMSParserWrongNumberOfAnswersException
from mock import Mock, patch
from mangrove.transport import TransportInfo
from messageprovider.exception_handler import handle
from messageprovider.handlers import create_failure_log
from messageprovider.message_handler import get_exception_message_for
from messageprovider.messages import SMS, exception_messages
from submission.models import DatawinnerLog

class TestExceptionHandler(unittest.TestCase):

    def setUp(self):
        self.request = dict(incoming_message='message',transport_info=TransportInfo(transport='SMS',source='123',destination='456'))
        self.request[FORM_CODE]='code'

    def test_should_handle_NumberNotRegisteredException(self):
        patcher = patch('messageprovider.handlers.create_failure_log')
        create_failure_log_mock = patcher.start()

        exception = NumberNotRegisteredException('1234312')

        expected_message = get_exception_message_for(exception, SMS)
        response = handle(exception, self.request)
        patcher.stop()

        self.assertEqual(expected_message, response)
        create_failure_log_mock.assert_called_with(expected_message,self.request)

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

    def test_should_create_failure_log(self):
        error_message = "error message"
        create_failure_log(error_message,self.request)
        log = DatawinnerLog.objects.all().order_by('-created_at')[0]
        self.assertEqual(error_message,log.error)
        self.assertEqual(self.request[FORM_CODE],log.form_code)
        self.assertEqual(self.request['transport_info'].source,log.from_number)
        self.assertEqual(self.request['transport_info'].destination,log.to_number)
        log.delete()

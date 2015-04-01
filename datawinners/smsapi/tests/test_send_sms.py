from unittest import TestCase
from django.http import HttpRequest, HttpResponse
import jsonpickle
from mock import Mock, patch, call, PropertyMock
from datawinners.accountmanagement.models import Organization
from datawinners.sms.models import MSG_TYPE_API
from datawinners.smsapi.send_sms import send_sms


def mock_auth(view, request, is_authenticated_func, authenticate_func, realm="", *args, **kwargs):
    return view(request, *args, **kwargs)


class TestSendSMSApi(TestCase):
    def test_send_sms(self):
        request = Mock(HttpRequest)
        type(request).raw_post_data = PropertyMock(
            return_value=jsonpickle.encode({"numbers": ["1212", "34334"], "message": "Hello world!"},
                                           unpicklable=False))
        with patch("datawinners.common.authorization.view_or_basicauth", mock_auth):
            with patch("datawinners.smsapi.send_sms.get_organization") as get_organization:
                mock_org = Mock(spec=Organization)
                mock_org.tel_number.return_value = "2222"
                mock_org.increment_sms_api_usage_count = Mock(return_value=None)
                get_organization.return_value = mock_org
                with patch("datawinners.scheduler.smsclient.SMSClient.send_sms") as send_sms_patch:
                    send_sms_patch.side_effect = [True, False]

                    response = send_sms(request)
                    self.assertTrue(isinstance(response, HttpResponse))
                    self.assertEqual(200, response.status_code)
                    self.assertDictEqual({"34334": "failure", "1212": "success"},
                                         jsonpickle.decode(response.content))
                    calls = [call("2222", '1212', "Hello world!", MSG_TYPE_API),
                             call("2222", '34334', "Hello world!", MSG_TYPE_API)]
                    self.assertEqual(send_sms_patch.call_args_list, calls)
                    mock_org.increment_sms_api_usage_count.assert_called_once_with()


    def test_should_return_bad_request_when_request_format_in_not_valid(self):
        request = Mock(HttpRequest)
        type(request).raw_post_data = PropertyMock(
            return_value=jsonpickle.encode({}, unpicklable=False))
        with patch("datawinners.common.authorization.view_or_basicauth", mock_auth):
            mock_org = Mock(spec=Organization)
            mock_org.tel_number.return_value = "2222"
            mock_org.increment_sms_api_usage_count = Mock(return_value=None)

            response = send_sms(request)
            self.assertTrue(isinstance(response, HttpResponse))
            self.assertEqual(400, response.status_code)


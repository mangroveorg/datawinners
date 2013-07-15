from unittest import TestCase
from django.http import HttpRequest, HttpResponse
import jsonpickle
from mock import Mock, patch, call


def mock_auth(view, request, is_authenticated_func, authenticate_func, realm="", *args, **kwargs):
    return view(request, *args, **kwargs)


class TestSendSMSApi(TestCase):
    def test_send_sms(self):
        request = Mock(HttpRequest)
        request.POST = {"number": "1212,34334", "message": "Hello world!"}
        with patch("datawinners.scheduler.smsclient.SMSClient.send_sms") as send_sms_patch:
            send_sms_patch.side_effect = [True, False]
            with patch("datawinners.feeds.authorization.view_or_basicauth", mock_auth):
                with patch("datawinners.smsapi.send_sms._get_org_number") as _get_org_number:
                    _get_org_number.return_value = "2222"
                    from datawinners.smsapi.send_sms import send_sms

                    response = send_sms(request)
                    self.assertTrue(isinstance(response, HttpResponse))
                    self.assertEqual(200, response.status_code)
                    self.assertDictEqual({"34334": "failure", "1212": "success"}, jsonpickle.decode(response.content))
                    calls = [call("2222", '1212', "Hello world!"), call("2222", '34334', "Hello world!")]
                    self.assertEqual(send_sms_patch.call_args_list,calls)


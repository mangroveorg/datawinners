import unittest
from mock import Mock
from datawinners.scheduler.vumiclient import VumiClient, VumiInvalidDestinationNumberException


class DummyConnection(object):

    def post(self,  *args, **kwargs):
        self.path = args[0]
        return Mock(status_code=200, content="{}");

class TestVumiClient(unittest.TestCase):

    def test_send_sms(self):
        connection = DummyConnection()
        client = VumiClient("user", "pass", connection)
        client.send_sms(to_msisdn="99992", from_msisdn="99991", message="test")

        self.assertEquals('/api/v1/sms/send.json', connection.path)

    def test_send_sms_to_same_number(self):
        connection = DummyConnection()
        client = VumiClient("user", "pass", connection)
        with self.assertRaises(VumiInvalidDestinationNumberException) as context:
            client.send_sms(to_msisdn="99991", from_msisdn="99991", message="test")

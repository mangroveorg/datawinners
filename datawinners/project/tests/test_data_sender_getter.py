from unittest import TestCase
from project.helper import DataSenderGetter

class TestDataSenderGetter(TestCase):
    org_id = 'SLX364903'

    def test_should_return_data_sender_list_by_organization_id(self):
        data_sender_list = DataSenderGetter().list_data_sender(self.org_id)
        self.assertEqual(5, len(data_sender_list))

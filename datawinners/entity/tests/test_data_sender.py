from django.utils.unittest.case import TestCase
from datawinners.entity.data_sender import remove_system_datasenders


class TestDataSender(TestCase):
    def test_remove_test_datasenders(self):
        ds_list = [{"short_code": "non-test"}, {"short_code":"test"}]
        remove_system_datasenders(ds_list)
        self.assertEqual(ds_list, [{"short_code": "non-test"}])
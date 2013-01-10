from unittest import TestCase
from project.data_sender import DataSender

class TestDataSender(TestCase):
    def test_should_return_TEST_data_sender_if_the_name_of_it_is_TEST(self):
        self.assertEqual(("TEST", "", "TEST"), DataSender("", "TEST", "").to_tuple())

    def test_should_data_sender_source_in_comma_seperated_format(self):
        self.assertEqual(('reporter', 'rep1', '123123,aa@bb.com'), DataSender(['123123', 'aa@bb.com'], 'reporter', 'rep1').to_tuple())

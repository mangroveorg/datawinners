from unittest import TestCase
from project.data_sender import DataSender

class TestDataSender(TestCase):
    def test_should_return_TEST_data_sender_if_the_name_of_it_is_TEST(self):
        self.assertEqual(("TEST", "", "TEST"), DataSender("", "TEST", "").to_tuple())
from unittest import TestCase
from datawinners.entity.datasender_search import datasender_count_with

from nose.plugins.attrib import attr


class TestDataSenderSearch(TestCase):

    @attr('integration_tests')
    def test_should_return_count_of_ds_with_matching_email_and_short_code(self):
        count = datasender_count_with(email='tester150411@gmail.com', short_code='rep276')

        self.assertEqual(count, 1)
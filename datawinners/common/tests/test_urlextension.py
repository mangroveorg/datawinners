import unittest
from datawinners.common.urlextension import append_query_strings_to_url


class TestUrlExtension(unittest.TestCase):

    def test_should_append_query_string_to_url(self):
        url = "http://somedomain/page/"

        url_with_query_string = append_query_strings_to_url(url, key1='value1', key2=True)

        self.assertEqual(url_with_query_string, "http://somedomain/page/?key2=True&key1=value1")

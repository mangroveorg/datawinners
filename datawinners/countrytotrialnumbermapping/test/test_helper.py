# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from countrytotrialnumbermapping import helper
from countrytotrialnumbermapping.models import Country

class TestHelper(unittest.TestCase):

    def test_country_should_convert_to_display_format(self):
        country1 = Country(country_name='Country1', country_code='1')
        country2 = Country(country_name='Country2', country_code='2')
        country3 = Country(country_name='Country3', country_code='3')
        actual_display_list = helper.get_countries_in_display_format([country1,country2,country3])
        expected_display_list = [
            ('Country1','Country1 (1)'),
            ('Country2','Country2 (2)'),
            ('Country3','Country3 (3)'),
        ]
        self.assertEqual(expected_display_list, actual_display_list)
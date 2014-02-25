# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from datawinners.countrytotrialnumbermapping import helper
from datawinners.countrytotrialnumbermapping.models import Network, Country

class TestHelper(unittest.TestCase):

    def test_country_should_convert_to_display_format(self):
        country1 = Country(country_name_en='Country1', country_code='1')
        country2 = Country(country_name_en='Country2', country_code='2')
        country3 = Country(country_name_en='Country3', country_code='3')
        actual_display_list = helper.get_countries_in_display_format([country1,country2,country3])
        expected_display_list = [
            ('Country1','Country1 (1)'),
            ('Country2','Country2 (2)'),
            ('Country3','Country3 (3)'),
        ]
        self.assertEqual(expected_display_list, actual_display_list)

    def test_should_create_new_trial_sms_number(self):
        current_numbers = helper.get_trial_numbers()
        new_number = "00000"
        self.assertFalse(new_number in current_numbers)
        network = Network(trial_sms_number=new_number, network_name="Airtel")
        network.save()
        self.assertTrue(new_number in helper.get_trial_numbers())
        network.delete()
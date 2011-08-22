# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from datawinners.location import utils

class TestUtils(unittest.TestCase):
    def test_should_map_location_groups_to_categories(self):
        input = {'Level1': ['a', 'b', 'c'], 'level2': ['df'], 'level3': ['1', '2'], 'level4': ['a']}
        expected_output = [{'label': 'a', 'category': 'Region'},
                {'label': 'b', 'category': 'Region'},
                {'label': 'c', 'category': 'Region'},
                {'label': 'df', 'category': 'District'},
                {'label': '1', 'category': 'Commune'},
                {'label': '2', 'category': 'Commune'},
                {'label': 'a', 'category': 'Fokontany'}]
        categories = utils.map_location_groups_to_categories(input, country='Madagascar')
        self.assertEquals(expected_output, categories)


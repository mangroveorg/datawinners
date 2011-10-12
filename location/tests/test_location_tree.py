# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from _collections import defaultdict
from django.test import TestCase
from nose.plugins.skip import SkipTest
from datawinners.location.LocationTree import get_location_groups_for_country, LocationTree

class TestLocationTree(TestCase):
    fixtures = ['test_location_level.json']
    def setUp(self):
        self.tree = LocationTree()

    def tearDown(self):
        pass

    def test_get_hierarchy_from_location(self):
        self.assertEqual(self.tree.get_hierarchy_path('Amboanjo'),
            ['madagascar', 'vatovavy fitovinany', 'manakara atsimo', 'amboanjo'])

    def test_should_return_same_value_if_not_in_path(self):
        self.assertEqual(['pune'], self.tree.get_hierarchy_path('pune'))

    def test_is_valid_location(self):
        self.assertTrue(self.tree._exists("amboanjo"))
        self.assertFalse(self.tree._exists("XYZ"))

    def test_should_get_location_hierarchy_for_geocode(self):
        self.assertEqual([u'madagascar', u'itasy', u'miarinarivo', u'ambatomanjaka', u'fkt ambaribe'],
                                                                                                     self.tree.get_location_hierarchy_for_geocode(
                                                                                                         lat=-18.777180,
                                                                                                         long=46.854321))
        self.assertFalse(self.tree._exists("XYZ"))

    def test_should_get_filtered_list_group_by_levels(self):
        expected_location_group = defaultdict(list)
        expected_location_group[u'LEVEL3'] = [u'AMBOANJO,MANAKARA ATSIMO,VATOVAVY FITOVINANY', u'AMBATOMANJAKA,MIARINARIVO,ITASY']
        actual_location_groups = get_location_groups_for_country(country="Madagascar", start_with="amb")
        self.assertEqual(expected_location_group, actual_location_groups)

    @SkipTest
    def test_should_get_centroid_for_location_based_on_level_given(self):
        self.assertEqual((46.8558925459, -18.762105675278256), self.tree.get_centroid(location='Ambatomanjaka',
                                                                                      level='3'))
        self.assertFalse(self.tree._exists("XYZ"))

    def test_should_return_none_for_location_unknown(self):
        self.assertEqual(None, self.tree.get_centroid(location='pune', level='3'))



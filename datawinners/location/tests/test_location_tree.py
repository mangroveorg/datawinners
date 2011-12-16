# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from _collections import defaultdict
from django.test import TestCase
from nose.plugins.skip import SkipTest
from datawinners.location.LocationTree import get_location_groups_for_country, LocationTree, get_location_hierarchy

class TestLocationTree(TestCase):
    fixtures = ['test_location_level.json']
    def setUp(self):
        self.tree = LocationTree()

    def tearDown(self):
        pass

    def test_get_hierarchy_from_location(self):
        self.assertEqual([u'AMBOANJO',u'MANAKARA ATSIMO',u'VATOVAVY FITOVINANY',u'Madagascar'], get_location_hierarchy('Amboanjo'))

    def test_should_return_same_value_if_not_in_path(self):
        self.assertEqual(['pune'], get_location_hierarchy('pune'))

    def test_should_get_location_hierarchy_for_geocode(self):
        self.assertEqual([u'madagascar', u'itasy', u'miarinarivo', u'ambatomanjaka', u'fkt ambaribe'],
                                                                                                     self.tree.get_location_hierarchy_for_geocode(
                                                                                                         lat=-18.777180,
                                                                                                         long=46.854321))
    def test_should_get_filtered_list_group_by_levels(self):
        expected_location_group = defaultdict(list)
        expected_location_group[u'LEVEL3'] = [u'AMBOANJO,MANAKARA ATSIMO,VATOVAVY FITOVINANY', u'AMBATOMANJAKA,MIARINARIVO,ITASY']
        actual_location_groups = get_location_groups_for_country(country="Madagascar", start_with="amb")
        self.assertEqual(expected_location_group, actual_location_groups)

    @SkipTest
    def test_should_get_centroid_for_location_based_on_level_given(self):
        self.assertEqual((46.8558925459, -18.762105675278256), self.tree.get_centroid(location='Ambatomanjaka',
                                                                                      level='3'))
    def test_should_return_none_for_location_unknown(self):
        self.assertEqual(None, self.tree.get_centroid(location='pune', level='3'))


        




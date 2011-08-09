# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from unittest.case import SkipTest
from datawinners.location.LocationTree import LocationTree, get_locations_for_country, get_location_groups_for_country

class TestLocationTree(unittest.TestCase):
    def setUp(self):
        self.tree = LocationTree()


    def tearDown(self):
        pass

    def test_load_tree(self):
        self.assertEqual('Madagascar', self.tree.countries[0])
        self.assertEqual(22, len(self.tree._get_next_level('Madagascar')))

    def test_get_hierarchy_from_location(self):
        self.assertEqual(self.tree.get_hierarchy_path('Amboanjo'),
            ['madagascar', 'vatovavy fitovinany', 'manakara atsimo', 'amboanjo'])

    def test_should_return_same_value_if_not_in_path(self):
        self.assertEqual(['pune'], self.tree.get_hierarchy_path('pune'))

    def test_is_valid_location(self):
        self.assertTrue(self.tree._exists("amboanjo"))
        self.assertFalse(self.tree._exists("XYZ"))

    def test_should_get_lowest_admin_location_for_geocode(self):
        self.assertEqual("fkt ambaribe", self.tree._get_location_for_geocode(lat=-18.777180, long=46.854321).lower())
        self.assertFalse(self.tree._exists("XYZ"))

    def test_should_get_location_hierarchy_for_geocode(self):
        self.assertEqual([u'madagascar', u'itasy', u'miarinarivo', u'ambatomanjaka', u'fkt ambaribe'], self.tree.get_location_hierarchy_for_geocode(lat=-18.777180, long=46.854321))
        self.assertFalse(self.tree._exists("XYZ"))

    def test_should_get_location_hierarchy_to_the_lowest_level_for_geocode(self):
        self.assertEqual([u'madagascar', u'analamanga', u'manjakandriana', u'ambohitrony', u'ambohijanaka'], self.tree.get_location_hierarchy_for_geocode(lat=-18.7415362448, long=47.7765977667))

    @SkipTest
    #TODO: USe this test and the related piece of code when the functionality gets used
    def test_should_get_filtered_list_lowest_levels(self):
        self.assertEqual(['ZOMA BEALOKA, ANTANANARIVO', 'ZAZAFOTSY, FIANARANTSOA'], get_locations_for_country(country="Madagascar", start_with="z"))

    def test_should_get_filtered_list_group_by_levels(self):
        expected_location_group={u'LEVEL3':[u'SOASERANA,MANJA,MENABE', u'SOASERANA,BETIOKY ATSIMO,ATSIMO ANDREFANA']}
        actual_location_groups = get_location_groups_for_country(country="Madagascar", start_with="soas")
        self.assertEqual(expected_location_group, actual_location_groups)

    @SkipTest
    def test_should_get_centroid_for_location_based_on_level_given(self):
        self.assertEqual((46.8558925459, -18.762105675278256), self.tree.get_centroid(location='Ambatomanjaka', level = '3'))
        self.assertFalse(self.tree._exists("XYZ"))

    def test_should_return_none_for_location_unknown(self):
        self.assertEqual(None, self.tree.get_centroid(location='pune', level = '3'))



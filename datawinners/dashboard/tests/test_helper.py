# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from unittest.case import SkipTest
from mock import Mock
from datawinners.dashboard import helper
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity


class TestHelper(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)

    def test_should_create_location_geojson(self):
        expected_geojson = '{"type": "FeatureCollection", "features": [{"geometry": {"type": "Point", "coordinates": [2, 1]}, "type": "Feature"}, {"geometry": {"type": "Point", "coordinates": [3, 1]}, "type": "Feature"}]}'
        entity1 = Entity(self.dbm, entity_type="waterpoint", location=["India", "MH", "Pune"], short_code="WP002",
                         geometry={'type': 'Point', 'coordinates': [1, 2]})
        entity2 = Entity(self.dbm, entity_type="waterpoint", location=["India", "MH", "Pune"], short_code="WP002",
                         geometry={'type': 'Point', 'coordinates': [1, 3]})
        entity_list = [entity1, entity2]
        resp = helper.create_location_geojson(entity_list)
        self.assertEqual(expected_geojson, resp, resp)

    def test_should_create_location_geojson_for_unknown_location(self):
        expected_geojson = '{"type": "FeatureCollection", "features": []}'
        entity1 = Entity(self.dbm, entity_type="Water Point", location=["India", "MH", "Pune"], short_code="WP002")
        entity_list = [entity1]
        self.assertEqual(expected_geojson, helper.create_location_geojson(entity_list))

    def test_should_not_raise_exception_if_no_location_or_geo_code_specified(self):
        entity = Entity(self.dbm, entity_type="Water Point", short_code="WP002")
        helper.create_location_geojson(entity_list=[entity])

    def test_should_not_raise_exception_if_coordinates_is_empty(self):
        expected_geojson = '{"type": "FeatureCollection", "features": [{"geometry": {"type": "Point", "coordinates": [3, 1]}, "type": "Feature"}]}'
        entity1 = Entity(self.dbm, entity_type="waterpoint", location=["India", "MH", "Pune"], short_code="WP002",
                         geometry={'type': 'Point', 'coordinates': []})
        entity2 = Entity(self.dbm, entity_type="waterpoint", location=["India", "MH", "Pune"], short_code="WP002",
                         geometry={'type': 'Point', 'coordinates': [1, 3]})
        entity_list = [entity1, entity2]
        self.assertEqual(expected_geojson, helper.create_location_geojson(entity_list))

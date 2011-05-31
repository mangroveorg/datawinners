# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from mock import Mock
from datawinners.maps import helper
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity


class TestHelper(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)

    def test_should_create_location_geojson(self):
        expected_geojson = '{"type": "FeatureCollection", "features": [{"geometry": {"type": "Point", "coordinates": [1, 2]}, "type": "Feature"}, {"geometry": {"type": "Point", "coordinates": [1, 3]}, "type": "Feature"}]}'
        entity1 = Entity(self.dbm, entity_type="Water Point", location=["India", "MH", "Pune"], short_code="WP002",
                         geometry={'type': 'Point', 'coordinates': [1, 2]})
        entity2 = Entity(self.dbm, entity_type="Water Point", location=["India", "MH", "Pune"], short_code="WP002",
                         geometry={'type': 'Point', 'coordinates': [1, 3]})
        entity_list = [entity1, entity2]
        self.assertEqual(expected_geojson, helper.create_location_geojson(entity_list))

# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from mock import Mock
from datawinners.maps import helper
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity

class TestHelper(unittest.TestCase):

    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)

    def test_should_create_location_list(self):
           expected_list = [{"short_code": "WP001", 'type': 'Point', 'latitude': 1, 'longitude':2}, {"short_code": "WP002", 'type': 'Point', 'latitude': 1, 'longitude':3}]
           entity1 = Entity(self.dbm, entity_type="Water Point", location=["India", "MH", "Pune"], short_code="WP001", geometry={'type': 'Point', 'coordinates': [1,2]})
           entity2 = Entity(self.dbm, entity_type="Water Point", location=["India", "MH", "Pune"], short_code="WP002", geometry={'type': 'Point', 'coordinates': [1,3]})
           entity_list = [entity1,entity2]
           self.assertListEqual(expected_list, helper.create_location_list(entity_list))
  
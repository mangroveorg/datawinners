# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from couchdb.client import Row
from django.utils import unittest
from mock import Mock

from datawinners.dashboard.views import _find_reporter_name
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Contact


class TestDashboard(unittest.TestCase):

    def test_should_get_return_reporter_name(self):
        row = Row()
        dbm = Mock(DatabaseManager)
        entity = Mock(Contact)
        entity.value.return_value = "ashwin"
        row.update({"value":{"owner_uid" : "123"}})
        dbm.get.return_value = entity
        reporter = _find_reporter_name(dbm, row)
        dbm.get.assert_called_once_with("123", Contact, False)
        self.assertEquals(reporter,"ashwin")



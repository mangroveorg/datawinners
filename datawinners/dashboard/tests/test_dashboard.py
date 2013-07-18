# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from couchdb.client import Row
from django.utils import unittest
from django.test import Client
from mock import Mock, call
from datawinners.dashboard.views import _find_reporter_name
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity


class TestDashboard(unittest.TestCase):

    fixtures = ['initial_data.json']
    def setUp(self):
        self.client = Client()

    def test_should_redirect_if_not_logged_in(self):
        response = self.client.post('/dashboard/')
        self.assertEquals(302, response.status_code)

    def test_should_render_dashboard_view_if_logged_in(self):
        self.client.login(username='tester150411@gmail.com',password='tester150411')
        response = self.client.get('/dashboard/')
        self.assertEquals(200, response.status_code)

    def test_should_get_return_reporter_name(self):
        row = Row()
        dbm = Mock(DatabaseManager)
        entity = Mock(Entity)
        entity.value.return_value = "ashwin"
        row.update({"value":{"owner_uid" : "123"}})
        dbm.get.return_value = entity
        reporter = _find_reporter_name(dbm, row)
        dbm.get.assert_called_once_with("123", Entity, False)
        self.assertEquals(reporter,"ashwin")



# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from couchdb.client import Row
from django.utils import unittest
from django.test import Client
from mock import Mock
from dashboard.views import _find_reporter_name
from mangrove.datastore.database import DatabaseManager

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
        nw_row = Row()
        nw_row.update({"value" : "ashwin"})
        row.update({"value":{"channel" : "sms", "source" : "5648"}})
        dbm = Mock(wraps=DatabaseManager)
        dbm.load_all_rows_in_view.return_value = [nw_row]
        reporter = _find_reporter_name(dbm, row)
        self.assertEquals(reporter,"ashwin")

    def test_should_return_telephone_no_if_reporter_has_updated_his_mobile_no(self):
        row = Row()
        row.update({"value": {"channel": "sms", "source": "5648"}})
        dbm = Mock(wraps=DatabaseManager)
        dbm.load_all_rows_in_view.return_value = []
        reporter = _find_reporter_name(dbm, row)
        self.assertEquals(reporter, "5648")


# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils import unittest
from django.test import Client
from django.test.client import RequestFactory
from datawinners.dashboard.views import dashboard

class TestDashboard(unittest.TestCase):

    fixtures = ['initial_data.json']
    def setUp(self):
        self.client_stub = Client()

    def test_should_redirect_if_not_logged_in(self):
        response = self.client_stub.post('/dashboard/')
        self.assertEquals(response.status_code, 302)

    def test_should_render_dashboard_view_if_logged_in(self):
        self.client_stub.post('/login/', {'username': 'tester150411@gmail.com', 'password': 'tester150411'})
        response = self.client_stub.get('/dashboard/')
        self.assertEquals(response.status_code,200)

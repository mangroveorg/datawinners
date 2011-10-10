# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils import unittest
from django.test import Client

class TestDashboard(unittest.TestCase):

    fixtures = ['initial_data.json']
    def setUp(self):
        self.client = Client()

    def test_should_redirect_if_not_logged_in(self):
        response = self.client.post('/dashboard/')
        self.assertEquals(response.status_code, 302)

    def test_should_render_dashboard_view_if_logged_in(self):
        self.client.login(username='tester150411@gmail.com',password='tester150411')
        response = self.client.get('/dashboard/')
        self.assertEquals(response.status_code,200)

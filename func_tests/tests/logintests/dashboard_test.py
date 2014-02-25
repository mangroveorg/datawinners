import unittest
from django.test import Client


class TestDashboard(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def test_should_redirect_if_not_logged_in(self):
        response = self.client.post('/dashboard/')
        self.assertEquals(302, response.status_code)

    def test_should_render_dashboard_view_if_logged_in(self):
        self.client.login(username='tester150411@gmail.com',password='tester150411')
        response = self.client.get('/dashboard/')
        self.assertEquals(200, response.status_code)
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from unittest2 import TestCase
from django.test import Client

class TestDashboard(TestCase):
    fixtures = ['initial_data.json']

    def test_should_redirect_if_not_logged_in(self):
        c = Client()
        response = c.post('/dashboard/')
        self.assertEquals(response.status_code, 302)

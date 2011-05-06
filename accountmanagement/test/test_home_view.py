# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from django.test.client import Client

class TestHomeView(unittest.TestCase):
    fixtures = ['initial_data.json']

    def test_home_view_should_redirect_if_not_logged_in(self):
        c = Client()
        response = c.post('/home')
        self.assertEquals(response.status_code,302)

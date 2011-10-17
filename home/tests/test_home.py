# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils import unittest
from django.test import Client

class TestHome(unittest.TestCase):

    def setUp(self):
        self.client_stub = Client()

    def test_should_render_home_view(self):
        response = self.client_stub.get('/home/')
        self.assertEquals(response.status_code,200)

    def test_should_render_link_to_trial_registration(self):
        for url in ['/home', '/home/en', '/home/fr'] :
            response = self.client_stub.get(url, follow=True)
            self.assertRegexpMatches(response.content, r'href="/register/trial"')


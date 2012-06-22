# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils import unittest
from django.test import Client

class TestUrls(unittest.TestCase):

    def setUp(self):
        self.client_stub = Client()

    def test_should_render_register_for_subscription_form(self):
        response = self.client_stub.get("/register/", follow = True)
        self.assertEquals(response.status_code, 200)

    def test_should_render_register_for_trial_form(self):
        response = self.client_stub.get("/register/trial", follow = True)
        self.assertEquals(response.status_code, 200)


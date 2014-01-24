from django.utils import unittest
from django.test import Client
from unittest.case import SkipTest


@SkipTest #functional_test
class TestAllData(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def  test_should_redirect_alldata_view_if_not_logged_in(self):
        response = self.client.get('/alldata/')
        self.assertEquals(response.status_code, 302)

    def test_should_render_alldata_view_if_logged_in(self):
        self.client.login(username='tester150411@gmail.com', password='tester150411')
        response = self.client.get('/alldata/')
        self.assertEquals(response.status_code, 200)

    def test_should_render_smart_phone_view_if_logged_in(self):
        self.client.login(username='datasender@test.com', password='111111')
        response = self.client.get('/smartphoneinstruction')
        self.assertEquals(response.status_code, 200)

    def test_should_redirect_smart_phone_view_if_not_logged_in(self):
        response = self.client.get('/smartphoneinstruction')
        self.assertEquals(response.status_code, 302)

    def test_should_render_entity_type_select_options_if_logged_in(self):
        self.client.login(username='tester150411@gmail.com', password='tester150411')
        response = self.client.get('/alldata/entities/clinic/')
        self.assertEquals(response.status_code, 200)

    def test_should_redirect_entity_type_select_options_request_if_not_logged_in(self):
        response = self.client.get('/alldata/entities/clinic/')
        self.assertEquals(response.status_code, 302)


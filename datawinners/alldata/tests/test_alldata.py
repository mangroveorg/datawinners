from django.utils import unittest
from django.test import Client

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

    def test_should_render_data_export_page_if_logged_in(self):
        self.client.login(username='tester150411@gmail.com', password='tester150411')
        response = self.client.get('/dataexport/')
        self.assertEquals(response.status_code, 200)

    def test_should_redirect_smart_phone_data_export_page_if_not_logged_in(self):
        response = self.client.get('/dataexport/')
        self.assertEquals(response.status_code, 302)

    def test_should_render_entity_type_select_options_if_logged_in(self):
        self.client.login(username='tester150411@gmail.com', password='tester150411')
        response = self.client.get('/alldata/entities/clinic/')
        self.assertEquals(response.status_code, 200)

    def test_should_redirect_entity_type_select_options_request_if_not_logged_in(self):
        response = self.client.get('/alldata/entities/clinic/')
        self.assertEquals(response.status_code, 302)

    def test_should_render_get_registgered_data_response_if_logged_in(self):
        self.client.login(username='tester150411@gmail.com', password='tester150411')
        response = self.client.get('/alldata/registereddata/clinic/')
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/alldata/registereddata/clinic/01-08-2012/')
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/alldata/registereddata/clinic/01-08-2012/03-08-2012/')
        self.assertEquals(response.status_code, 200)


    def test_should_return_404_response_status_when_date_format_is_invalid(self):
        self.client.login(username='tester150411@gmail.com', password='tester150411')

        response = self.client.get('/alldata/registereddata/clinic/2/')
        self.assertEquals(response.status_code, 404)

        response = self.client.get('/alldata/registereddata/clinic/01-08-2012/03082012/')
        self.assertEquals(response.status_code, 404)

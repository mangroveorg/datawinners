from django.utils import unittest
from django.test import Client


class TestEntity(unittest.TestCase):


    def setUp(self):
        self.client_stub = Client()

    def  test_should_redirect_datasender_create_if_not_logged_in(self):
        response = self.client_stub.get('/entity/datasender/create')
        self.assertEquals(response.status_code, 302)

    def test_should_render_datasender_create_view_if_logged_in(self):
        self.client_stub.post('/login/', {'username': 'tester150411@gmail.com', 'password': 'tester150411'})
        response = self.client_stub.get('/entity/datasender/create')
        self.assertEquals(response.status_code,200)

from django.utils import unittest
from django.test import Client


class TestEntityLoggedIn(unittest.TestCase):


    def setUp(self):
        self.client_stub = Client()
        self.client_stub.post('/login/', {'username': 'tester150411@gmail.com', 'password': 'tester150411'})

    def test_should_render_datasender_create_view_if_logged_in(self):
        response = self.client_stub.get('/entity/datasender/create')
        self.assertEquals(response.status_code,200)

    def test_should_render_subject_create_view_if_logged_in(self):
        response = self.client_stub.get('/entity/subject/create')
        self.assertEquals(response.status_code,200)

    def test_should_render_entity_datasenders_view_if_logged_in(self):
        response = self.client_stub.get('/entity/datasenders/')
        self.assertEquals(response.status_code,200)




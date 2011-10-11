from django.contrib.auth.models import User
from django.utils import unittest
from django.test import Client
import json

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

#TODO Refactor this code and apply django tests to it (currently using nose tests)
    def test_should_add_data_sender_with_appropriate_email(self):
        response = self.client_stub.post('/entity/webuser/create',{'post_data' : json.dumps([{"email":"a1@a1.com","reporter_id":"rep4"},{"email":"a2@a2.com","reporter_id":"test"}])})
        self.assertEquals(response.status_code,200)

        response = self.client_stub.post('/entity/webuser/create',{'post_data' : json.dumps([{"email":"a1@a1.com.com","reporter_id":"rep9"}])})
        self.assertEquals(response.status_code,400)

        users = User.objects.filter(email='a1@a1.com')
        for user in users:
            user.delete()
        users = User.objects.filter(email='a2@a2.com')
        for user in users:
            user.delete()

    def test_should_render_all_subjects_view_if_logged_in(self):
        response = self.client_stub.get('/entity/subjects/')
        self.assertEquals(response.status_code,200)




import random
import string
from unittest.case import SkipTest
from django.test import TestCase
from django.test import Client
import json

class TestEntityLoggedIn(TestCase):

    def setUp(self):
        self.client = Client()
        self.client.login(username = 'tester150411@gmail.com', password = 'tester150411')

    def test_should_render_datasender_create_view_if_logged_in(self):
        response = self.client.get('/entity/datasender/create')
        self.assertEquals(response.status_code,200)

    def test_should_render_subject_create_view_if_logged_in(self):
        response = self.client.get('/entity/subject/create/clinic/')
        self.assertEquals(response.status_code,200)

    def test_should_render_entity_datasenders_view_if_logged_in(self):
        response = self.client.get('/entity/datasenders/')
        self.assertEquals(response.status_code,200)

    def test_should_add_data_sender_with_appropriate_email(self):
        email1 = ''.join(random.choice(string.letters) for x in range(10)) + '@gmail.com'
        email2 = ''.join(random.choice(string.letters) for x in range(10)) + '@gmail.com'
        response = self.client.post('/entity/webuser/create/',{'post_data' : json.dumps([{"email": email1,"reporter_id":"rep4"},{"email": email2,"reporter_id":"test"}])})
        self.assertEquals(response.status_code,200)

        response = self.client.post('/entity/webuser/create/',{'post_data' : json.dumps([{"email":email1,"reporter_id":"rep4"}])})
        self.assertEquals(response.status_code,200)

    def test_should_render_all_subjects_view_if_logged_in(self):
        response = self.client.get('/entity/subjects/')
        self.assertEquals(response.status_code,200)

    def test_should_associate_datasender(self):
        ids = "test"
        project_id = "fe84831af56111e0aa085c260a236744"
        response = self.client.post('/entity/associate/',{'project_id' : project_id,'ids' : ids})
        self.assertEquals(response.status_code,200)

    def test_should_disassociate_datasender(self):
        ids = "test"
        project_id = "fe84831af56111e0aa085c260a236744"
        response = self.client.post('/entity/disassociate/',{'project_id' : project_id,'ids' : ids})
        self.assertEquals(response.status_code,200)

    @SkipTest
    def test_should_create_subject_type(self):
        entity_type_regex = "abc"
        response = self.client.post('/entity/type/create',{'entity_type_regex' : entity_type_regex})
        self.assertEquals(response.status_code,200)

        entity_type_regex = "client"
        response = self.client.post('/entity/type/create',{'entity_type_regex' : entity_type_regex})
        self.assertEquals(response.status_code,200)

        entity_type_regex = ""
        response = self.client.post('/entity/type/create',{'entity_type_regex' : entity_type_regex})
        self.assertEquals(response.status_code,200)
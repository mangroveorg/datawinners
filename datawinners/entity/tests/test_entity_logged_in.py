from unittest.case import SkipTest
from django.test import TestCase
from django.test import Client


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
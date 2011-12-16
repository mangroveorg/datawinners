from django.test import TestCase
from django.test import Client



class TestEntityNotLoggedIn(TestCase):


    def setUp(self):
        self.client_stub = Client()

    def  test_should_redirect_datasender_create_if_not_logged_in(self):
        response = self.client_stub.get('/entity/datasender/create')
        self.assertEquals(response.status_code, 302)

    def  test_should_redirect_subject_create_if_not_logged_in(self):
        response = self.client_stub.get('/entity/subject/create')
        self.assertEquals(response.status_code, 302)

    def  test_should_redirect_entity_datasenders_if_not_logged_in(self):
        response = self.client_stub.get('entity/datasenders')
        self.assertEquals(response.status_code, 302)

    def  test_should_redirect_all_subjects_view_if_not_logged_in(self):
        response = self.client_stub.get('entity/subjects')
        self.assertEquals(response.status_code, 302)




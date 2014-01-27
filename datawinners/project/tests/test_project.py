from unittest.case import SkipTest
from django.test import TestCase
from django.test import Client

class TestProject(TestCase):
    def setUp(self):
        self.client = Client()

    def test_should_render_project_view_if_not_logged_in(self):
        response = self.client.post('/project/')
        self.assertEquals(response.status_code, 302)

    def test_should_render_project_wizard_view_if_not_logged_in(self):
        response = self.client.post('/project/wizard/create/')
        self.assertEquals(response.status_code, 302)

    def test_should_render_questionnaire_view_if_not_logged_in(self):
        response = self.client.get('project/questionnaire')
        self.assertEquals(response.status_code, 302)

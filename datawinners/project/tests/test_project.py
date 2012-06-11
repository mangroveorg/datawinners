import json
from unittest.case import SkipTest
from django.test import TestCase
from django.test import Client


class TestProject(TestCase):

    def setUp(self):
        self.client = Client()

    def test_should_render_project_view_if_not_logged_in(self):
        response = self.client.post('/project/')
        self.assertEquals(response.status_code,302)

    def test_should_render_project_view_if_logged_in(self):
        self.client.login(username = 'tester150411@gmail.com', password = 'tester150411')
        response = self.client.post('/project/')
        self.assertEquals(response.status_code,200)

    def test_should_render_project_wizard_view_if_not_logged_in(self):
        response = self.client.post('/project/wizard/create/')
        self.assertEquals(response.status_code,302)

    def test_should_render_questionnaire_view_if_not_logged_in(self):
        project_id = 'fe84831af56111e0aa085c260a236744'
        response = self.client.get('project/questionnaire')
        self.assertEquals(response.status_code,302)

    @SkipTest
    def test_should_render_questionary_view_if_logged_in(self):
        self.client.login(username = 'tester150411@gmail.com', password = 'tester150411')
        project_id = 'fe84831af56111e0aa085c260a236744'
        response = self.client.get('project/questionnaire',{'project_id' : project_id})
        self.assertEquals(response.status_code, 200)

    def test_should_render_sms_preview_if_logged_in(self):
        self.client.login(username = 'tester150411@gmail.com', password = 'tester150411')
        response = self.client.post('/project/sms_preview', {"questionnaire-code": "q01",
                                                            "question-set": '{}',
                                                            "profile_form": '{"name":"project_name", "entity_type":"clinic", "language":"en"}',
                                                            'project_state': "Test"})
        self.assertEqual(response.status_code, 200)

    def test_should_render_web_preview_if_logged_in(self):
        self.client.login(username = 'tester150411@gmail.com', password = 'tester150411')
        response = self.client.post('/project/web_preview', {"questionnaire-code": "q01",
                                                             "question-set": '{}',
                                                             "profile_form": '{"name":"project_name", "entity_type":"clinic", "language":"en"}',
                                                             'project_state': "Test"})
        self.assertEqual(response.status_code, 200)

    def test_should_render_smart_phone_preview_if_logged_in(self):
        self.client.login(username = 'tester150411@gmail.com', password = 'tester150411')
        response = self.client.post('/project/smart_phone_preview')
        self.assertEqual(response.status_code, 200)

    def test_should_render_questionnaire_sms_preview_if_logged_in(self):
        self.client.login(username = 'tester150411@gmail.com', password = 'tester150411')
        response = self.client.post('/project/questionnaire_sms_preview')
        self.assertEqual(response.status_code, 200)
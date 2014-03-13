import unittest
from django.test import Client, TestCase
from datawinners.utils import _get_email_template_name_for_reset_password
from datawinners.tests.data import DEFAULT_TEST_USER, DEFAULT_TEST_PASSWORD

class TestAccountManagement(TestCase):

    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_should_get_email_template_for_reset_password_for_english(self):
        template_name = _get_email_template_name_for_reset_password('en')
        self.assertEqual('registration/password_reset_email_en.html', template_name)

    def test_should_get_email_template_for_reset_password_for_french(self):
        template_name = _get_email_template_name_for_reset_password('fr')
        self.assertEqual('registration/password_reset_email_fr.html', template_name)

    def test_should_render_register_view(self):
        response = self.client.post('/register/')
        self.assertEquals(response.status_code, 200)

    def test_should_render_login_view(self):
        response = self.client.post('/login/')
        self.assertEquals(response.status_code,200)

    def test_should_render_password_reset_view(self):
        response = self.client.post('/password/reset/')
        self.assertEquals(response.status_code,200)

    def test_should_render_register_view(self):
        response = self.client.post('/registration_complete')
        self.assertEquals(response.status_code, 200)

    def test_should_render_admin_view(self):
        response = self.client.post('/admin/')
        self.assertEquals(response.status_code, 200)

    def test_should_render_account_view_if_not_logged_in(self):
        response = self.client.post('/account/')
        self.assertEquals(response.status_code, 302)

    def test_should_render_account_view_if_logged_in(self):
        self.login_with_default_test_user()
        response = self.client.get('/account/')
        self.assertEquals(200,response.status_code)

    def test_should_render_profile_view_if_not_logged_in(self):
        response = self.client.get('/profile/')
        self.assertEquals(302,response.status_code)

    def test_should_render_profile_view_if_logged_in(self):
        self.login_with_default_test_user()
        response = self.client.get('/profile/')
        self.assertEquals(response.status_code,200)

    def test_should_render_account_users_view_if_not_logged_in(self):
        response = self.client.post('/account/users/')
        self.assertEquals(response.status_code, 302)

    def test_should_render_account_users_view_if_logged_in(self):
        self.login_with_default_test_user()
        response = self.client.get('/account/users/')
        self.assertEquals(response.status_code, 200)

    def test_should_not_render_account_user_new_view_if_not_logged_in(self):
        response = self.client.get('/account/user/new/')
        self.assertEquals(response.status_code, 302)

    def test_should_render_account_user_new_view_if_logged_in(self):
        self.login_with_default_test_user()
        response = self.client.post('/account/user/new/')
        self.assertEquals(response.status_code, 200)

    def login_with_default_test_user(self):
        self.client.login(username=DEFAULT_TEST_USER, password=DEFAULT_TEST_PASSWORD)

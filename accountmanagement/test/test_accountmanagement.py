from django.test import TestCase
from django.test import Client
from nose.plugins.skip import SkipTest

class TestAccountManagement(TestCase):
    def setUp(self):
        self.client = Client()

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

    @SkipTest
    def test_should_render_account_view_if_logged_in(self):
        self.client.login(username = 'tester150411@gmail.com', password = 'tester150411')
        response = self.client.post('/account/')
#        self.assertRedirects(response,'/dashboard/')
        self.assertEquals(response.status_code, 302)
#        self.assertContains(response,'Dashboard')
#        self.assertContains(response,'Dashboard')

    def test_should_render_profile_view_if_not_logged_in(self):
        response = self.client.get('/profile/')
        self.assertEquals(response.status_code,302)

    def test_should_render_profile_view_if_not_logged_in(self):
        self.client.login(username = 'tester150411@gmail.com', password = 'tester150411')
        response = self.client.get('/profile/')
        self.assertEquals(response.status_code,200)

    @SkipTest
    def test_should_render_account_users_view_if_not_logged_in(self):
        response = self.client.post('/account/users/')
        self.assertEquals(response.status_code, 302)
#        self.assertRedirects(response,'/login')

    def test_should_render_account_users_view_if_logged_in(self):
        self.client.login(username = 'tester150411@gmail.com', password = 'tester150411')
        response = self.client.post('/account/users/')
        self.assertEquals(response.status_code, 302)

    @SkipTest
    def test_should_render_account_user_new_view_if_not_logged_in(self):
        response = self.client.post('/account/user/new/')
        self.assertEquals(response.status_code, 302)
#        self.assertContains(response,'Sign In to Your Account on DataWinners')

    @SkipTest
    def test_should_render_account_user_new_view_if_logged_in(self):
        self.client.login(username = 'tester150411@gmail.com', password = 'tester150411')
        response = self.client.post('/account/user/new/')
#        self.assertRedirects(response,'/dashboard/',status_code=302,target_status_code=200)
        self.assertEquals(response.status_code, 302)
#        self.assertContains(response,'Dashboard')
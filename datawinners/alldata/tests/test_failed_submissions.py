from django.test import Client, TestCase


class TestFailedSubmissions(TestCase):

    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def  test_should_redirect_failed_submissions_view_if_not_logged_in(self):
        response = self.client.get('/allfailedsubmissions')
        self.assertEquals(response.status_code, 302)

    def test_should_render_failed_submissions_view_if_logged_in(self):
        self.client.login(username= 'tester150411@gmail.com', password= 'tester150411')
        response = self.client.get('/allfailedsubmissions')
        self.assertEquals(response.status_code,200)

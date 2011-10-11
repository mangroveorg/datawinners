from django.utils import unittest
from django.test import Client


class TestFailedSubmissions(unittest.TestCase):


    def setUp(self):
        self.client_stub = Client()

    def  test_should_redirect_failed_submissions_view_if_not_logged_in(self):
        response = self.client_stub.get('/allfailedsubmissions')
        self.assertEquals(response.status_code, 302)

    def test_should_render_failed_submissions_view_if_logged_in(self):
        self.client_stub.post('/login/', {'username': 'tester150411@gmail.com', 'password': 'tester150411'})
        response = self.client_stub.get('/allfailedsubmissions')
        self.assertEquals(response.status_code,200)

from unittest import TestCase
import urllib2
from django.http import HttpRequest
from mock import Mock, patch

patch('django_digest.decorators.httpdigest', lambda x: x).start()
from datawinners.feeds.views import feed_entries

class TestFeedView(TestCase):
    def test_error_when_form_code_is_not_present(self):
        request = Mock(spec=HttpRequest)
        response = feed_entries(request, None)
        self.assertEqual(400, response.status_code)
        self.assertEqual('Invalid form code provided', response.content)

    def test_error_when_form_code_is_empty(self):
        request = Mock(spec=HttpRequest)
        response = feed_entries(request, "     ")
        self.assertEqual(400, response.status_code)
        self.assertEqual('Invalid form code provided', response.content)

    def test_error_when_start_date_not_provided(self):
        request = HttpRequest()
        response = feed_entries(request, "cli001")
        self.assertEqual(400, response.status_code)
        self.assertEqual('Invalid Start Date provided', response.content)

    def test_error_when_start_date_is_empty(self):
        request = HttpRequest()
        request.GET['start_date'] = "     "

        response = feed_entries(request, "cli001")
        self.assertEqual(400, response.status_code)
        self.assertEqual('Invalid Start Date provided', response.content)


    def test_error_when_start_date_is_not_in_correct_format(self):
        request = HttpRequest()
        request.GET['start_date'] = urllib2.quote("21/12/2001".encode("utf-8"))
        response = feed_entries(request, "cli001")
        self.assertEqual(400, response.status_code)
        self.assertEqual('Invalid Start Date provided', response.content)

    def test_error_when_end_date_not_provided(self):
        request = HttpRequest()
        request.GET['start_date'] = urllib2.quote("21-12-2001 12:12:57".encode("utf-8"))
        response = feed_entries(request, "cli001")
        self.assertEqual(400, response.status_code)
        self.assertEqual('Invalid End Date provided', response.content)

    def test_error_when_end_date_is_empty(self):
        request = HttpRequest()
        request.GET['start_date'] = urllib2.quote("21-12-2001 12:12:57".encode("utf-8"))
        request.GET['end_date'] = "   "

        response = feed_entries(request, "cli001")
        self.assertEqual(400, response.status_code)
        self.assertEqual('Invalid End Date provided', response.content)


    def test_error_when_end_date_is_not_in_correct_format(self):
        request = HttpRequest()
        request.GET['start_date'] = urllib2.quote("21-12-2001 12:12:57".encode("utf-8"))
        request.GET['end_date'] = urllib2.quote("21-12-2001".encode("utf-8"))

        response = feed_entries(request, "cli001")
        self.assertEqual(400, response.status_code)
        self.assertEqual('Invalid End Date provided', response.content)



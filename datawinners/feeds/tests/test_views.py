from unittest import TestCase
import urllib2
from django.http import HttpRequest
from mock import Mock, patch, PropertyMock
from mangrove.datastore.database import DatabaseManager, View

http_basic_patch = patch('datawinners.feeds.basic_auth.httpbasic', lambda x: x)
http_basic_patch.start()
datasender_patch = patch('datawinners.feeds.utils.is_not_datasender', lambda x: x)
datasender_patch.start()
from datawinners.feeds.views import feed_entries, _parse_date

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

    def test_error_when_end_date_is_less_than_start_date(self):
        request = HttpRequest()
        request.GET['start_date'] = urllib2.quote("21-12-2001 12:12:57".encode("utf-8"))
        request.GET['end_date'] = urllib2.quote("21-12-2001 12:12:56".encode("utf-8"))

        response = feed_entries(request, "cli001")
        self.assertEqual(400, response.status_code)
        self.assertEqual('End Date provided is less than Start Date', response.content)

    def test_view_queried_with_limit_on_entries(self):
        request = HttpRequest()
        request.GET['start_date'] = urllib2.quote("21-12-2001 12:12:57".encode("utf-8"))
        request.GET['end_date'] = urllib2.quote("31-12-2001 12:12:56".encode("utf-8"))
        request.user = 'someuser'
        with patch('datawinners.feeds.views.get_feeds_database') as get_feeds_database:
            dbm = Mock(spec=DatabaseManager)
            get_feeds_database.return_value = dbm
            view = Mock(spec=View)
            type(dbm).view = PropertyMock(return_value=view)
            mock_view = Mock(spec=View)
            type(view).questionnaire_feed = PropertyMock(return_value=mock_view)
            mock_view.return_value = []
            feed_entries(request, 'cli001')

            mock_view.assert_called_once_with(startkey=['cli001', _parse_date('21-12-2001 12:12:57')],
                                              endkey=['cli001', _parse_date('31-12-2001 12:12:56')],
                                              limit=10000)


http_basic_patch.stop()
datasender_patch.stop()
import unittest

from django_digest.test import Client
from mock import Mock, patch, PropertyMock
from django.contrib.auth.models import User
from django.http import HttpRequest
from datawinners.tests.data import DEFAULT_TEST_USER, DEFAULT_TEST_PASSWORD
from datawinners.accountmanagement.views import users


class TestUserActivityLogDetails(unittest.TestCase):
    def test_should_render_user_activity_log_details_when_deleting_multiple_users(self):
        from django.contrib.auth.models import User
        from datawinners.accountmanagement.views import user_activity_log_details

        user_a = User(first_name="firstA", last_name="lastA", email="emailA")
        user_b = User(first_name="firstB", last_name="lastB", email="emailB")
        result = user_activity_log_details([user_a, user_b])

        self.assertEqual("Name: firstA lastA<br>Email: emailA<br><br>Name: firstB lastB<br>Email: emailB", result)

    def test_SMS_API_Users_not_shown_on_user_list_page(self):
        client = Client()
        client.login(username=DEFAULT_TEST_USER, password=DEFAULT_TEST_PASSWORD)
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.get(username="tester150411@gmail.com")

        with patch('datawinners.accountmanagement.views.User') as user_class:
            with patch('datawinners.accountmanagement.views.RequestContext') as context:
                with patch("datawinners.accountmanagement.views.render_to_response") as render_response_patch:
                    objects = Mock()
                    type(user_class).objects = PropertyMock(return_value=objects)
                    users(request)
                    objects.exclude.assert_called_once_with(groups__name__in=['Data Senders', 'SMS API Users'])

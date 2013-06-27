from unittest import TestCase
from django.http import HttpResponse
from mock import Mock, PropertyMock
from accountmanagement.models import NGOUserProfile
from datawinners.feeds.authorization import is_not_datasender


class TestAuthorization(TestCase):
    def test_should_restrict_datasender_from_accessing_view(self):
        def foo(request):
            return HttpResponse(status=200)

        foo = is_not_datasender(foo)
        mock_request = Mock()
        mock_user = Mock(spec=NGOUserProfile)
        type(mock_user).reporter = PropertyMock(return_value=True)
        mock_request.user.get_profile.return_value = mock_user
        response = foo(mock_request)
        self.assertEquals(400, response.status_code)
        self.assertEquals("You do not have the required permissions to access "
                          "this information. Please contact your system administrator", response.content)

    def test_should_allow_others(self):
        def foo(request):
            return HttpResponse(content="welcome", status=200)

        foo = is_not_datasender(foo)
        mock_request = Mock()
        mock_user = Mock(spec=NGOUserProfile)
        type(mock_user).reporter = PropertyMock(return_value=False)
        mock_request.user.get_profile.return_value = mock_user
        response = foo(mock_request)
        self.assertEquals(200, response.status_code)
        self.assertEquals("welcome", response.content)

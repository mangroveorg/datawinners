# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.alldata import helper
from datawinners.project.couch_view_helper import get_all_projects


class TestHelper(unittest.TestCase):

    def setUp(self):
        self.database_manager = helper.get_database_manager
        self.all_projects = get_all_projects
        helper.get_database_manager = stub_get_database_manager

    def _get_normal_user(self):
        user = Mock(User)
        normal_profile = Mock(NGOUserProfile)
        normal_profile.reporter = False
        user.get_profile.return_value = normal_profile
        return user

    def _get_reporter_user(self):
        user = Mock(User)
        reporter_profile = Mock(NGOUserProfile)
        reporter_profile.reporter = True
        reporter_profile.reporter_id = 'something'
        user.get_profile.return_value = reporter_profile
        return user

    # def test_should_return_all_projects(self):
    #     user = self._get_normal_user()
    #     with patch("datawinners.alldata.helper.get_all_projects") as get_all_projects_mock:
    #         get_all_projects_mock.return_value = {"project_name": "hello world"}
    #         projects = get_all_project_for_user(user)
    #     assert projects["project_name"] == "hello world"

    # def test_should_return_all_projects_for_user(self):
    #     user = self._get_reporter_user()
    #     get_all_projects = stub_get_all_projects_for_reporter
    #     projects = get_all_project_for_user(user)
    #     assert projects["project_name"] == "hello world"

    def test_should_return_disabled_and_display_none_for_reporter(self):
        user = self._get_reporter_user()
        disabled, hide = helper.get_visibility_settings_for(user)
        assert disabled  == 'disable_link_for_reporter'
        assert hide == 'none'

    def test_should_return_enabled_and_display_for_other(self):
        user = self._get_normal_user()
        disabled, hide = helper.get_visibility_settings_for(user)
        assert hide  == ""
        assert disabled == ""

    def test_should_return_DataSubmission_for_reporter(self):
        user = self._get_reporter_user()
        request = MagicMock()
        organization = MagicMock(spec=Organization)
        with patch('datawinners.alldata.helper.get_organization') as mock_get_organization:
            mock_get_organization.return_value = organization
            request.user = user
            assert helper.get_page_heading(request) == 'Data Submission'

    def test_should_return_AllData_for_trial_and_pro_account(self):
        user = self._get_normal_user()
        request = MagicMock()
        organization = MagicMock(spec=Organization)
        organization.is_pro_sms = False
        with patch('datawinners.alldata.helper.get_organization') as mock_get_organization:
            mock_get_organization.return_value = organization
            request.user = user
            assert helper.get_page_heading(request) == 'Questionnaires'

    def test_should_return_AllData_for_pro_sms_account(self):
        user = self._get_normal_user()
        request = MagicMock()
        organization = MagicMock(spec=Organization)
        organization.is_pro_sms = True
        with patch('datawinners.alldata.helper.get_organization') as mock_get_organization:
            mock_get_organization.return_value = organization
            request.user = user
            assert helper.get_page_heading(request) == 'Questionnaires & Polls'

    def tearDown(self):
        get_all_projects = self.all_projects
        helper.get_database_manager = self.database_manager

def stub_get_database_manager(*args):
    return Mock()

def stub_get_all_projects_for_reporter(*args):
    assert args[0] is not None
    assert args[1] is not None
    return {"project_name": "hello world"}

def stub_get_all_projects(*args):
    assert args[0] is not None
    return {"project_name": "hello world"}

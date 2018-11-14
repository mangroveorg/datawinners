# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from mock import Mock, patch, MagicMock
from datawinners.accountmanagement.models import Organization
from datawinners.alldata import helper
from datawinners.common.tests.common_test_utils import get_reporter_user, get_project_manager, get_ngo_admin, \
    get_extended_user
from datawinners.project.couch_view_helper import get_all_projects

class TestHelper(unittest.TestCase):

    def setUp(self):
        self.database_manager = helper.get_database_manager
        self.all_projects = get_all_projects
        helper.get_database_manager = stub_get_database_manager

    @patch('datawinners.alldata.helper.remove_poll_questionnaires')
    @patch('datawinners.alldata.helper.get_all_projects')
    def test_should_return_all_projects_for_user_as_reporter(self, mock_get_all_projects, mock_remove_poll_questionnaires):
        user = get_reporter_user()
        all_projects_for_user = [{'_id': 'd3456cc', 'name': 'test questionnaire'}]
        all_projects = [{'value': {'_id':'d3456cc', 'name':'test questionnaire'}},
                {'value': {'_id':'d3456ccxyx', 'name':'test questionnaire', 'is_poll': True}}]

        mock_get_all_projects.return_value = all_projects
        mock_remove_poll_questionnaires.return_value = all_projects_for_user
        self.assertEqual(helper.get_all_project_for_user(user), all_projects_for_user)
        assert helper.get_all_project_for_user(user) == all_projects_for_user
    
    @patch('datawinners.alldata.helper.get_questionnaires_for_user')
    @patch('datawinners.alldata.helper.get_all_projects')
    def test_should_return_all_projects_for_user_as_project_manager(self, mock_get_all_projects, mock_get_questionnaires_for_user):
        user = get_project_manager()
        all_projects_for_user = [{'_id':'d3456cc', 'name':'test questionnaire','is_project_manager': True}, {'_id':'256cc', 'name':'2nd questionnaire','is_project_manager': True}]
        questionnaires_as_ds = [{'value':{'_id':'d3456cc', 'name':'test questionnaire'}}, {'value':{'_id':'ds_question', 'name':'Data sender questionnaire'}}]
        expected_questionnaires = [{'_id':'d3456cc', 'name':'test questionnaire','is_project_manager': True}, {'_id':'256cc', 'name':'2nd questionnaire','is_project_manager': True}, {'_id':'ds_question', 'name':'Data sender questionnaire'}]
        mock_get_all_projects.return_value = questionnaires_as_ds
        mock_get_questionnaires_for_user.return_value = all_projects_for_user
        questionnaires_to_display = helper.get_all_project_for_user(user)
        self.assertEqual(len(questionnaires_to_display), 3)
        self.assertEqual(questionnaires_to_display, expected_questionnaires)

    def test_should_return_all_projects_for_user_as_ngo_admin(self):
        user = get_ngo_admin()
        all_projects = [{'value':{'_id':'d3456cc', 'name':'test questionnaire'}}, {'value':{'_id':'256cc', 'name':'2nd questionnaire'}}]
        all_projects_expected = [{'_id':'d3456cc', 'name':'test questionnaire'}, {'_id':'256cc', 'name':'2nd questionnaire'}]
        with patch('datawinners.alldata.helper.get_all_projects') as mock_get_all_projects:
            mock_get_all_projects.return_value = all_projects
            assert helper.get_all_project_for_user(user) == all_projects_expected

    def test_should_return_all_projects_for_user_as_extended_user(self):
        user = get_extended_user()
        all_projects = [{'value':{'_id':'d3456cc', 'name':'test questionnaire'}}, {'value':{'_id':'256cc', 'name':'2nd questionnaire'}}]
        all_projects_expected = [{'_id':'d3456cc', 'name':'test questionnaire'}, {'_id':'256cc', 'name':'2nd questionnaire'}]
        with patch('datawinners.alldata.helper.get_all_projects') as mock_get_all_projects:
            mock_get_all_projects.return_value = all_projects
            assert helper.get_all_project_for_user(user) == all_projects_expected

    def test_should_return_disabled_and_display_none_for_reporter(self):
        user = get_reporter_user()
        disabled, hide = helper.get_visibility_settings_for(user)
        assert disabled == 'disable_link_for_reporter'
        assert hide == 'none'

    def test_should_return_enabled_and_display_for_other(self):
        user = get_project_manager()
        disabled, hide = helper.get_visibility_settings_for(user)
        assert hide == ""
        assert disabled == ""

    def test_should_return_DataSubmission_for_reporter(self):
        user = get_reporter_user()
        request = MagicMock()
        organization = MagicMock(spec=Organization)
        with patch('datawinners.alldata.helper.get_organization') as mock_get_organization:
            mock_get_organization.return_value = organization
            request.user = user
            assert helper.get_page_heading(request) == 'Data Submission'

    def test_should_return_AllData_for_trial_and_pro_account(self):
        user = get_project_manager()
        request = MagicMock()
        organization = MagicMock(spec=Organization)
        organization.is_pro_sms = False
        with patch('datawinners.alldata.helper.get_organization') as mock_get_organization:
            mock_get_organization.return_value = organization
            request.user = user
            assert helper.get_page_heading(request) == 'Questionnaires'

    def test_should_return_AllData_for_pro_sms_account(self):
        user = get_project_manager()
        request = MagicMock()
        organization = MagicMock(spec=Organization)
        organization.is_pro_sms = True
        with patch('datawinners.alldata.helper.get_organization') as mock_get_organization:
            mock_get_organization.return_value = organization
            request.user = user
            assert helper.get_page_heading(request) == 'Questionnaires & Polls'

def stub_get_database_manager(*args):
    return Mock()

def stub_get_all_projects_for_reporter(*args):
    assert args[0] is not None
    assert args[1] is not None
    return {"project_name": "hello world"}

def stub_get_all_projects(*args):
    assert args[0] is not None
    return {"project_name": "hello world"}

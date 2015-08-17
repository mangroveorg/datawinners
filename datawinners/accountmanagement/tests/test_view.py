import unittest
from django.test import TestCase

from mock import Mock, patch, MagicMock
from datawinners.accountmanagement.views import associate_user_with_all_projects_of_organisation, \
    associate_user_with_projects, make_user_data_sender_with_project
from mangrove.form_model.project import Project
from mangrove.datastore.user_permission import UserPermission
from django.test import Client
from datawinners.tests.data import DEFAULT_TEST_PASSWORD, DEFAULT_TEST_USER
from django.contrib.auth.models import User
from datawinners.accountmanagement.models import NGOUserProfile
from mangrove.datastore.database import DatabaseManager

class TestUserActivityLogDetails(TestCase):

    fixtures = ['test_data.json']

    def test_should_render_user_activity_log_details_when_deleting_multiple_users(self):
        from django.contrib.auth.models import User
        from datawinners.accountmanagement.views import user_activity_log_details

        user_a = User(first_name="firstA", last_name="lastA", email="emailA")
        user_b = User(first_name="firstB", last_name="lastB", email="emailB")
        result = user_activity_log_details([user_a, user_b])

        self.assertEqual("Name: firstA lastA<br>Email: emailA<br><br>Name: firstB lastB<br>Email: emailB", result)

class TestUserAssociationToProject(unittest.TestCase):
    def test_should_associate_user_to_existing_projects(self):
        dbm = Mock()
        with patch('datawinners.accountmanagement.views.Project') as ProjectMock:
            with patch("datawinners.accountmanagement.views.get_all_projects") as get_all_projects_mock:
                with patch("datawinners.accountmanagement.views.update_datasender_index_by_id") as update_datasender_index_by_id_mock:
                    get_all_projects_mock.return_value = [{'value':{'_id': 'id1'}}]
                    project_mock = MagicMock(spec=Project)
                    ProjectMock.get.return_value = project_mock
                    project_mock.data_senders = []

                    associate_user_with_all_projects_of_organisation(dbm, 'rep123')

                    project_mock.associate_data_sender_to_project.assert_called_once_with(dbm, ['rep123'])

    def test_should_associate_user_to_projects(self):
        dbm = Mock()
        with patch('datawinners.accountmanagement.views.Project') as ProjectMock:
            with patch("datawinners.accountmanagement.views.get_all_projects") as get_all_projects_mock:
                with patch("datawinners.accountmanagement.views.update_datasender_index_by_id") as update_datasender_index_by_id_mock:
                    with patch('datawinners.accountmanagement.views.UserPermission') as UPMock:
                        get_all_projects_mock.return_value = [{'value':{'_id': 'id1'}}]
                        project_mock = MagicMock(spec=Project)
                        user_permission_mock = MagicMock(spec=UserPermission)
                        UPMock.return_value = user_permission_mock
                        ProjectMock.get.return_value = project_mock
                        project_mock.data_senders = []

                        associate_user_with_projects(dbm, 'rep123', '1', ['q1', 'q2'])

                        project_mock.associate_data_sender_to_project.assert_called_with(dbm, ['rep123'])
                        assert user_permission_mock.save.called, 'Save on User Permissions was expected to be called ' \
                                                                 'but was not called'

class TestViews(TestCase):

    fixtures = ['test_data.json']

    @patch('datawinners.accountmanagement.views.update_datasender_index_by_id')
    @patch('datawinners.accountmanagement.views.Project')
    @patch('datawinners.accountmanagement.views.get_all_projects')
    @patch('datawinners.accountmanagement.views.make_user_as_a_datasender')
    @patch('datawinners.accountmanagement.views.NGOUserProfile')
    @patch('datawinners.accountmanagement.views.User')
    @patch('datawinners.accountmanagement.views.get_database_manager')
    def test_should_create_new_user_as_extended_user(self, manager_def_mock, user_mock, ngouserprofile_def_mock, make_user_as_datasender_mock, get_all_projects_mock, project_mock, update_datasender_index_by_id_mock):
        client = Client()
        login_success = client.login(username=DEFAULT_TEST_USER, password=DEFAULT_TEST_PASSWORD)
        assert login_success, 'Unable to proceed with the test, since unable to login'
        data = {'title': 'administrator', 'full_name': 'Henry', 'username': 'henry@mailinator.com',
                                     'mobile_phone': '7889522', 'role': 'Extended Users'}
        manager_mock,user_saved_mock, ngo_user_profile_mock, questionnaire_mock  = self._base_dependency_setup(manager_def_mock, user_mock, ngouserprofile_def_mock, project_mock)
        questionnaires = [{'value':{'_id':'d3456cc', 'name':'test questionnaire'}}, {'value':{'_id':'ds_question', 'name':'Data sender questionnaire'}}]
        get_all_projects_mock.return_value = questionnaires
        make_user_as_datasender_mock.return_value = 'rep123'
        response = client.post('/account/user/new/', data)
        self.assertEquals(response.status_code, 201)
        self.assertTrue(user_saved_mock.save.called)
        self.assertTrue(ngo_user_profile_mock.save.called)
        questionnaire_mock.associate_data_sender_to_project.assert_called_with(manager_mock,['rep123'])
        update_datasender_index_by_id_mock.assert_called_with('rep123',manager_mock)
        
    @patch('datawinners.accountmanagement.views.UserPermission')   
    @patch('datawinners.accountmanagement.views.update_datasender_index_by_id')
    @patch('datawinners.accountmanagement.views.Project')
    @patch('datawinners.accountmanagement.views.get_all_projects')
    @patch('datawinners.accountmanagement.views.make_user_as_a_datasender')
    @patch('datawinners.accountmanagement.views.NGOUserProfile')
    @patch('datawinners.accountmanagement.views.User')
    @patch('datawinners.accountmanagement.views.get_database_manager')
    def test_should_create_new_user_as_project_manager(self, manager_def_mock, user_mock, ngouserprofile_def_mock, make_user_as_datasender_mock, get_all_projects_mock, project_mock, update_datasender_index_by_id_mock, userpermission_def_mock):
        client = Client()
        login_success = client.login(username=DEFAULT_TEST_USER, password=DEFAULT_TEST_PASSWORD)
        assert login_success, 'Unable to proceed with the test, since unable to login'
        data = {'title': 'project manager', 'full_name': 'Bob', 'username': 'bob@mailinator.com',
                                     'mobile_phone': '7889523', 'role': 'Project Managers', 'selected_questionnaires[]': ['q1', 'q2', 'q3']}
        manager_mock,user_saved_mock, ngo_user_profile_mock, questionnaire_mock  = self._base_dependency_setup(manager_def_mock, user_mock, ngouserprofile_def_mock, project_mock)
        user_saved_mock.id = '1234'
        make_user_as_datasender_mock.return_value = 'rep123'
        user_permission_mock = MagicMock(spec=UserPermission)
        userpermission_def_mock.return_value = user_permission_mock
        
        response = client.post('/account/user/new/', data)

        self.assertEquals(response.status_code, 201)
        self.assertTrue(user_saved_mock.save.called)
        self.assertTrue(ngo_user_profile_mock.save.called)
        questionnaire_mock.associate_data_sender_to_project.assert_called_with(manager_mock,['rep123'])
        update_datasender_index_by_id_mock.assert_called_with('rep123',manager_mock)
        self.assertTrue(user_permission_mock.save.called)

    def _base_dependency_setup(self, manager_def_mock, user_mock, ngouserprofile_def_mock, project_mock):
        manager_mock = MagicMock(spec=DatabaseManager)
        manager_def_mock.return_value = manager_mock
        user_saved_mock = MagicMock(spec=User)
        user_mock.objects.create_user.return_value = user_saved_mock
        ngo_user_profile_mock = MagicMock(spec=NGOUserProfile)
        ngouserprofile_def_mock.return_value = ngo_user_profile_mock
        questionnaire_mock = MagicMock(spec=Project)
        project_mock.get.return_value = questionnaire_mock

        return manager_mock, user_saved_mock, ngo_user_profile_mock, questionnaire_mock
        
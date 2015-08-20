import unittest
from django.test import TestCase

from mock import Mock, patch, MagicMock
from datawinners.accountmanagement.forms import UserProfileForm,\
    EditUserProfileForm
from datawinners.accountmanagement.views import associate_user_with_all_projects_of_organisation, \
    associate_user_with_projects, make_user_data_sender_with_project
from mangrove.form_model.project import Project
from mangrove.datastore.user_permission import UserPermission
from django.test import Client
from datawinners.tests.data import DEFAULT_TEST_PASSWORD, DEFAULT_TEST_USER
from django.contrib.auth.models import User, Group
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from mangrove.datastore.database import DatabaseManager
from django.db.models.fields.related import ManyToManyField


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
                with patch(
                        "datawinners.accountmanagement.views.update_datasender_index_by_id") as update_datasender_index_by_id_mock:
                    get_all_projects_mock.return_value = [{'value': {'_id': 'id1'}}]
                    project_mock = MagicMock(spec=Project)
                    ProjectMock.get.return_value = project_mock
                    project_mock.data_senders = []

                    associate_user_with_all_projects_of_organisation(dbm, 'rep123')

                    project_mock.associate_data_sender_to_project.assert_called_once_with(dbm, ['rep123'])

    def test_should_associate_user_to_projects(self):
        dbm = Mock()
        with patch('datawinners.accountmanagement.views.Project') as ProjectMock:
            with patch("datawinners.accountmanagement.views.get_all_projects") as get_all_projects_mock:
                with patch(
                        "datawinners.accountmanagement.views.update_datasender_index_by_id") as update_datasender_index_by_id_mock:
                    with patch('datawinners.accountmanagement.views.UserPermission') as UPMock:
                        get_all_projects_mock.return_value = [{'value': {'_id': 'id1'}}]
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

    @patch('datawinners.accountmanagement.views.UserProfileForm')
    @patch('datawinners.accountmanagement.views.update_datasender_index_by_id')
    @patch('datawinners.accountmanagement.views.Project')
    @patch('datawinners.accountmanagement.views.get_all_projects')
    @patch('datawinners.accountmanagement.views.make_user_as_a_datasender')
    @patch('datawinners.accountmanagement.views.NGOUserProfile')
    @patch('datawinners.accountmanagement.views.User')
    @patch('datawinners.accountmanagement.views.get_database_manager')
    def test_should_create_new_user_as_extended_user(self, manager_def_mock, user_mock, ngouserprofile_def_mock,
                                                     make_user_as_datasender_mock, get_all_projects_mock, project_mock,
                                                     update_datasender_index_by_id_mock, user_profile_form_def_mock):
        client = self._login_as_super_admin()
        data = {'title': 'administrator', 'full_name': 'Henry', 'username': 'henry@mailinator.com',
                'mobile_phone': '7889522', 'role': 'Extended Users'}
        manager_mock, user_saved_mock, ngo_user_profile_mock, questionnaire_mock = self._base_dependency_setup(
            manager_def_mock, user_mock, ngouserprofile_def_mock, project_mock)
        user_profile_form_mock = self._mock_form(user_profile_form_def_mock, UserProfileForm)
        questionnaires = [{'value': {'_id': 'd3456cc', 'name': 'test questionnaire'}},
                          {'value': {'_id': 'ds_question', 'name': 'Data sender questionnaire'}}]
        get_all_projects_mock.return_value = questionnaires
        make_user_as_datasender_mock.return_value = 'rep123'
        response = client.post('/account/user/new/', data)
        self.assertEquals(response.status_code, 201)
        self.assertTrue(user_saved_mock.save.called)
        self.assertTrue(ngo_user_profile_mock.save.called)
        questionnaire_mock.associate_data_sender_to_project.assert_called_with(manager_mock, ['rep123'])
        update_datasender_index_by_id_mock.assert_called_with('rep123', manager_mock)

    @patch('datawinners.accountmanagement.views.UserProfileForm')
    @patch('datawinners.accountmanagement.views.UserPermission')
    @patch('datawinners.accountmanagement.views.update_datasender_index_by_id')
    @patch('datawinners.accountmanagement.views.Project')
    @patch('datawinners.accountmanagement.views.get_all_projects')
    @patch('datawinners.accountmanagement.views.make_user_as_a_datasender')
    @patch('datawinners.accountmanagement.views.NGOUserProfile')
    @patch('datawinners.accountmanagement.views.User')
    @patch('datawinners.accountmanagement.views.get_database_manager')
    def test_should_create_new_user_as_project_manager(self, manager_def_mock, user_mock, ngouserprofile_def_mock,
                                                       make_user_as_datasender_mock, get_all_projects_mock,
                                                       project_mock, update_datasender_index_by_id_mock,
                                                       userpermission_def_mock, user_profile_form_def_mock):
        client = Client()
        login_success = client.login(username=DEFAULT_TEST_USER, password=DEFAULT_TEST_PASSWORD)
        assert login_success, 'Unable to proceed with the test, since unable to login'
        data = {'title': 'project manager', 'full_name': 'Bob', 'username': 'bob@mailinator.com',
                'mobile_phone': '7889523', 'role': 'Project Managers', 'selected_questionnaires[]': ['q1', 'q2', 'q3']}
        manager_mock, user_saved_mock, ngo_user_profile_mock, questionnaire_mock = self._base_dependency_setup(
            manager_def_mock, user_mock, ngouserprofile_def_mock, project_mock)
        user_profile_form_mock = self._mock_form(user_profile_form_def_mock, UserProfileForm)
        user_saved_mock.id = '1234'
        make_user_as_datasender_mock.return_value = 'rep123'
        user_permission_mock = MagicMock(spec=UserPermission)
        userpermission_def_mock.return_value = user_permission_mock

        response = client.post('/account/user/new/', data)

        self.assertEquals(response.status_code, 201)
        self.assertTrue(user_saved_mock.save.called)
        self.assertTrue(ngo_user_profile_mock.save.called)
        questionnaire_mock.associate_data_sender_to_project.assert_called_with(manager_mock, ['rep123'])
        update_datasender_index_by_id_mock.assert_called_with('rep123', manager_mock)
        self.assertTrue(user_permission_mock.save.called)

    @patch('datawinners.accountmanagement.views.get_organization')
    @patch('datawinners.accountmanagement.views.update_corresponding_datasender_details')
    @patch('datawinners.accountmanagement.views.EditUserProfileForm')
    @patch('datawinners.accountmanagement.views.UserPermission')
    @patch('datawinners.accountmanagement.views.update_datasender_index_by_id')
    @patch('datawinners.accountmanagement.views.Project')
    @patch('datawinners.accountmanagement.views.get_all_projects')
    @patch('datawinners.accountmanagement.views.make_user_as_a_datasender')
    @patch('datawinners.accountmanagement.views.NGOUserProfile')
    @patch('datawinners.accountmanagement.views.User')
    @patch('datawinners.accountmanagement.views.get_database_manager')
    def test_should_change_role_pm_to_admin(self, manager_def_mock, user_mock, ngouserprofile_def_mock,
                                                       make_user_as_datasender_mock, get_all_projects_mock,
                                                       project_mock, update_datasender_index_by_id_mock,
                                                       userpermission_def_mock, edit_user_profile_form_def_mock,
                                                       update_corresponding_datasender_details_def_mock,
                                                       get_organization_def_mock):
        client = self._login_as_super_admin()
        manager_mock, user_saved_mock, ngo_user_profile_mock, questionnaire_mock = self._base_dependency_setup(
            manager_def_mock, user_mock, ngouserprofile_def_mock, project_mock)
        
        user_profile_form_mock = self._mock_form(edit_user_profile_form_def_mock, EditUserProfileForm)
        user_profile_form_mock.cleaned_data = {'full_name':'Bob', 'title': 'project manager', 'mobile_phone': '7889523'}
        get_organization_def_mock.return_value = MagicMock(spec=Organization)
        ngo_user_profile_mock.mobile_phone = '44556677'
        ngo_user_profile_mock.reporter_id = 'rep123'
        group_mock = MagicMock(spec=Group)
        group_mock.name = "Project Managers"
        groups_mock = MagicMock()
        groups_mock.clear = MagicMock()
        #
        user_saved_mock.groups = groups_mock
        user_saved_mock.id = 23
        all_groups_def_mock = MagicMock()
        groups_mock.all = all_groups_def_mock
        all_groups_def_mock.return_value = [group_mock]
        data = {'title': 'project manager', 'full_name': 'Bob', 'username': 'bob@mailinator.com',
                'mobile_phone': '7889523', 'role': 'Extended Users'}
        response = client.post('/account/users/23/edit', data)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(user_saved_mock.save.called)
        self.assertTrue(ngo_user_profile_mock.save.called)
        update_corresponding_datasender_details_def_mock.assert_called_with(user_saved_mock, ngo_user_profile_mock, '44556677')

    def _login_as_super_admin(self):
        client = Client()
        login_success = client.login(username=DEFAULT_TEST_USER, password=DEFAULT_TEST_PASSWORD)
        assert login_success, 'Unable to proceed with the test, since unable to login'
        return client
        
    def _base_dependency_setup(self, manager_def_mock, user_mock, ngouserprofile_def_mock, project_mock):
        manager_mock = MagicMock(spec=DatabaseManager)
        manager_def_mock.return_value = manager_mock
        user_saved_mock = MagicMock(spec=User)
        user_saved_mock.username = 'bob@mailinator.com'
        user_mock.objects.create_user.return_value = user_saved_mock
        user_mock.objects.get.return_value = user_saved_mock
        ngo_user_profile_mock = MagicMock(spec=NGOUserProfile)
        ngouserprofile_def_mock.return_value = ngo_user_profile_mock
        ngouserprofile_def_mock.objects.get.return_value = ngo_user_profile_mock
        questionnaire_mock = MagicMock(spec=Project)
        project_mock.get.return_value = questionnaire_mock

        return manager_mock, user_saved_mock, ngo_user_profile_mock, questionnaire_mock

    def _mock_form(self, def_mock, form_type):
        user_profile_form_mock = MagicMock(spec=form_type)
        user_profile_form_mock.is_valid.return_value = True
        user_profile_form_mock.errors = {}
        def_mock.return_value = user_profile_form_mock
        return user_profile_form_mock
    
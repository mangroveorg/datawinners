import unittest
from datawinners.accountmanagement.user_tasks import link_user_to_all_projects
from django.contrib.auth.models import User
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.main.database import get_database_manager
from mock import Mock, patch

class TestLinkUser(unittest.TestCase):

    def setUp(self):
        self.new_user = User(first_name="First", last_name="Last", username="a@b.c")
        self.new_user.save()
        from datawinners.accountmanagement.models import Organization
        org_id = Organization.objects.all()[0].org_id
        self.ngouser = NGOUserProfile(user=self.new_user, org_id=org_id, reporter_id="ds406")
        self.ngouser.save()

    @patch('datawinners.accountmanagement.user_tasks.make_user_data_sender_with_project')
    @patch('datawinners.accountmanagement.user_tasks.get_all_projects')
    @patch('datawinners.accountmanagement.user_tasks.get_database_manager')
    def test_should_link_user_as_datasender_to_all_project(self, get_database_manager_mock, get_all_projects_mock,
                                                           make_user_data_sender_with_project_mock):
        all_projects = [{'value':{'datasenders':["ds406", "rep011"], "_id": "27348932184297"}}]
        get_database_manager_mock.return_value = "dbm"
        get_all_projects_mock.return_value = all_projects
        link_user_to_all_projects.apply(args=(self.new_user.id,)).get()
        get_database_manager_mock.assert_called_with(self.new_user)
        make_user_data_sender_with_project_mock.assert_called_with("dbm", "ds406", "27348932184297")


    def tearDown(self):
        self.ngouser.delete()
        self.new_user.delete()
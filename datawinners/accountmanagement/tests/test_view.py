import unittest
from django.test import TestCase

from mock import Mock, patch, MagicMock
from datawinners.accountmanagement.views import associate_user_with_existing_project
from mangrove.form_model.project import Project


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

                    associate_user_with_existing_project(dbm, 'rep123')

                    project_mock.associate_data_sender_to_project.assert_called_once_with(dbm, ['rep123'])
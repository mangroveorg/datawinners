from collections import OrderedDict
from unittest import TestCase
from mock import MagicMock, patch
from datawinners.common.tests.common_test_utils import get_project_manager, get_ngo_admin, get_extended_user
from datawinners.project.couch_view_helper import get_project_id_name_map_for_user
from mangrove.datastore.database import DatabaseManager


class TestProjectHelper(TestCase):
    @patch('datawinners.project.couch_view_helper.get_questionnaires_for_user')
    def test_should_return_project_id_name_map_for_pm_in_alphabetical_order_of_names(self,
                                                                                     mock_get_questionnaires_for_user):
        dbm = MagicMock(spec=DatabaseManager)
        user_mock = get_project_manager()
        user_mock.id = 3
        all_projects_for_user = [{'_id': 'd3456cc', 'name': 'test questionnaire', 'is_project_manager': True},
                                 {'_id': '256cc', 'name': '2nd questionnaire', 'is_project_manager': True}]
        mock_get_questionnaires_for_user.return_value = all_projects_for_user
        project_id_name_map = get_project_id_name_map_for_user(dbm, user_mock)
        expected_project_id_map = OrderedDict([('256cc', '2nd questionnaire'), ('d3456cc', 'test questionnaire')])
        self.assertDictEqual(expected_project_id_map, project_id_name_map)

    def test_should_return_project_id_name_map_for_ngo_admin_in_alphabetical_order_of_names(self):
        self._assert_project_id_name_map_for(get_ngo_admin())

    def test_should_return_project_id_name_map_for_extended_user_in_alphabetical_order_of_names(self):
        self._assert_project_id_name_map_for(get_extended_user())

    def _assert_project_id_name_map_for(self, user_mock):
        dbm = MagicMock(spec=DatabaseManager)
        user_mock.id = 3
        all_projects_for_user = [{'value': {'_id': 'd3456cc', 'name': 'test questionnaire'}},
                                 {'value': {'_id': '256cc', 'name': '2nd questionnaire'}}]
        dbm.load_all_rows_in_view.return_value = all_projects_for_user
        project_id_name_map = get_project_id_name_map_for_user(dbm, user_mock)
        expected_project_id_map = OrderedDict([('256cc', '2nd questionnaire'), ('d3456cc', 'test questionnaire')])
        self.assertDictEqual(expected_project_id_map, project_id_name_map)

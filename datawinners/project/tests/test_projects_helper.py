from collections import OrderedDict
from unittest import TestCase
from mock import Mock
from datawinners.project.couch_view_helper import get_project_id_name_map
from mangrove.datastore.database import DatabaseManager


class TestProjectHelper(TestCase):
    def test_should_return_project_id_name_map_in_alphabetical_order_of_names(self):
        dbm = Mock(spec=DatabaseManager)
        rows = [{'value': {'id': 'some_id2', 'name': 'b'}}, {'value': {'id': 'some_id1', 'name': 'a'}},
                {'value': {'id': 'some_id3', 'name': 'Aa'}}]
        dbm.load_all_rows_in_view.return_value = rows

        project_id_name_map = get_project_id_name_map(dbm)

        expected_project_id_map = OrderedDict([('some_id1', 'a'), ('some_id3', 'Aa'), ('some_id2', 'b')])

        self.assertDictEqual(expected_project_id_map, project_id_name_map)
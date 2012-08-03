from unittest.case import TestCase
from mangrove.datastore.database import DatabaseManager
from mock import Mock
from mock import patch
from dataextraction.helper import get_data_by_subject


class TestHelper(TestCase):

    def test_should_return_data_of_subject_by_type_and_id(self):
        dbm = Mock(spec=DatabaseManager)
        with patch.object(dbm, "load_all_rows_in_view") as load_all_rows_in_view:
            load_all_rows_in_view.return_value =  [{"id": "1", "key": [["clinic"], "cid001", 1],
                                                   "value": {"What is the GPS code for clinic?": [79.2, 20.34567]}},
                    {"id": "1", "key": [["clinic"], "cid001", 1],
                     "value": {"What is the GPS code for clinic?": [79.2, 20.34567]}}]
            subject_data = get_data_by_subject(dbm, "clinic", "cid001")
            self.assertTrue(isinstance(subject_data, list))
            self.assertEqual(2, len(subject_data))


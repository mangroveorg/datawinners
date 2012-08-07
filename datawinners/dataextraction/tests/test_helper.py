from unittest.case import TestCase
from mangrove.datastore.database import DatabaseManager
from mock import Mock
from mock import patch
from dataextraction.models import DataExtractionResult
from dataextraction.helper import get_data_for_subject, encapsulate_data_for_subject, get_data_for_form, encapsulate_data_for_form

class TestHelper(TestCase):

    def test_should_return_data_of_subject_by_type_and_id(self):
        dbm = Mock(spec=DatabaseManager)
        with patch.object(dbm, "load_all_rows_in_view") as load_all_rows_in_view:
            load_all_rows_in_view.return_value =  [{"id": "1", "key": [["clinic"], "cid001", 1],
                                                   "value": {"What is the GPS code for clinic?": [79.2, 20.34567]}},
                    {"id": "1", "key": [["clinic"], "cid001", 1],
                     "value": {"What is the GPS code for clinic?": [79.2, 20.34567]}}]
            subject_data = get_data_for_subject(dbm, "clinic", "cid001")
            self.assertTrue(isinstance(subject_data, list))
            self.assertEqual(2, len(subject_data))

    def test_should_return_data_of_subject_by_type_and_id_and_date(self):
        dbm = Mock(spec=DatabaseManager)
        with patch.object(dbm, "load_all_rows_in_view") as load_all_rows_in_view:
            load_all_rows_in_view.return_value =  [{"id": "1", "key": [["clinic"], "cid001", 1],
                                                   "value": {"What is the GPS code for clinic?": [79.2, 20.34567]}},
                    {"id": "1", "key": [["clinic"], "cid001", 1],
                     "value": {"What is the GPS code for clinic?": [79.2, 20.34567]}}]
            subject_data = get_data_for_subject(dbm, "clinic", "cid001", "06-08-2012", "06-08-2012")
            self.assertTrue(isinstance(subject_data, list))
            self.assertEqual(2, len(subject_data))

    def test_should_return_data_of_subject_by_type_and_id_and_start_date(self):
        dbm = Mock(spec=DatabaseManager)
        with patch.object(dbm, "load_all_rows_in_view") as load_all_rows_in_view:
            load_all_rows_in_view.return_value =  [{"id": "1", "key": [["clinic"], "cid001", 1],
                                                   "value": {"What is the GPS code for clinic?": [79.2, 20.34567]}},
                    {"id": "1", "key": [["clinic"], "cid001", 1],
                     "value": {"What is the GPS code for clinic?": [79.2, 20.34567]}}]
            subject_data = get_data_for_subject(dbm, "clinic", "cid001", "06-08-2012")
            self.assertTrue(isinstance(subject_data, list))
            self.assertEqual(2, len(subject_data))

    def test_should_return_data_with_success_status_and_value_for_subject(self):
        dbm = Mock()
        with patch("dataextraction.helper.get_data_for_subject") as get_data_for_subject:
            get_data_for_subject.return_value = [ {"What is the GPS code for clinic?": [79.2, 20.34567]},
                    {"What is the GPS code for clinic?": [79.2, 20.34567]}]
            with patch("dataextraction.helper.entity_type_already_defined") as entity_type_already_defined:
                entity_type_already_defined.return_value = True
                with patch("dataextraction.helper.check_if_subject_exists") as check_if_subject_exists:
                    check_if_subject_exists.return_value = True
                    data_for_subject = encapsulate_data_for_subject(dbm, "clinic", "cid001")
                    self.assertIsInstance(data_for_subject, DataExtractionResult)
                    self.assertTrue(data_for_subject.success)
                    self.assertEqual(2, len(data_for_subject.value))

    def test_should_return_data_with_success_status_set_to_false_when_pass_in_wrong_subject_type(self):
        dbm = Mock()
        with patch("dataextraction.helper.get_data_for_subject") as get_data_for_subject:
            get_data_for_subject.return_value = [ {"What is the GPS code for clinic?": [79.2, 20.34567]},
                    {"What is the GPS code for clinic?": [79.2, 20.34567]}]
            with patch("dataextraction.helper.entity_type_already_defined") as entity_type_already_defined:
                entity_type_already_defined.return_value = False
                not_defined_entity = "clinic"
                data_for_subject = encapsulate_data_for_subject(dbm, not_defined_entity, "cid001")
                self.assertIsInstance(data_for_subject, DataExtractionResult)
                self.assertFalse(data_for_subject.success)
                self.assertEqual(data_for_subject.message, "Entity type [%s] is not defined." % not_defined_entity)
                self.assertEqual(0, len(data_for_subject.value))

    def test_should_return_data_with_success_status_set_to_false_when_pass_in_wrong_subject_id(self):
        dbm = Mock()
        with patch("dataextraction.helper.get_data_for_subject") as get_data_for_subject:
            get_data_for_subject.return_value = [ {"What is the GPS code for clinic?": [79.2, 20.34567]},
                    {"What is the GPS code for clinic?": [79.2, 20.34567]}]
            with patch("dataextraction.helper.entity_type_already_defined") as entity_type_already_defined:
                entity_type_already_defined.return_value = True
                with patch("dataextraction.helper.check_if_subject_exists") as check_if_subject_exists:
                    check_if_subject_exists.return_value = False
                    not_registered_subject = "cid001"
                    data_for_subject = encapsulate_data_for_subject(dbm, "clinic", not_registered_subject)
                    self.assertIsInstance(data_for_subject, DataExtractionResult)
                    self.assertFalse(data_for_subject.success)
                    self.assertEqual(data_for_subject.message, "Entity [%s] is not registered." % not_registered_subject)
                    self.assertEqual(0, len(data_for_subject.value))


    def test_should_return_data_with_success_status_set_to_false_when_pass_in_wrong_date_format(self):
        dbm = Mock()
        with patch("dataextraction.helper.get_data_for_subject") as get_data_for_subject:
            get_data_for_subject.return_value = [ {"What is the GPS code for clinic?": [79.2, 20.34567]},
                    {"What is the GPS code for clinic?": [79.2, 20.34567]}]
            with patch("dataextraction.helper.entity_type_already_defined") as entity_type_already_defined:
                entity_type_already_defined.return_value = True
                with patch("dataextraction.helper.check_if_subject_exists") as check_if_subject_exists:
                    check_if_subject_exists.return_value = True
                    data_for_subject = encapsulate_data_for_subject(dbm, "clinic", "cid001", "03082012", "06082012")
                    self.assertIsInstance(data_for_subject, DataExtractionResult)
                    self.assertFalse(data_for_subject.success)
                    self.assertEqual(data_for_subject.message, "The format of start and end date should be DD-MM-YYYY. Example: 25-12-2011")
                    self.assertEqual(0, len(data_for_subject.value))

    def test_should_return_data_with_success_status_set_to_false_when_pass_in_wrong_date(self):
        dbm = Mock()
        with patch("dataextraction.helper.get_data_for_subject") as get_data_for_subject:
            get_data_for_subject.return_value = [ {"What is the GPS code for clinic?": [79.2, 20.34567]},
                    {"What is the GPS code for clinic?": [79.2, 20.34567]}]
            with patch("dataextraction.helper.entity_type_already_defined") as entity_type_already_defined:
                entity_type_already_defined.return_value = True
                with patch("dataextraction.helper.check_if_subject_exists") as check_if_subject_exists:
                    check_if_subject_exists.return_value = True
                    data_for_subject = encapsulate_data_for_subject(dbm, "clinic", "cid001", "06-08-2012", "03-08-2012")
                    self.assertIsInstance(data_for_subject, DataExtractionResult)
                    self.assertFalse(data_for_subject.success)
                    self.assertEqual(data_for_subject.message, "Start date must before end date.")
                    self.assertEqual(0, len(data_for_subject.value))

    def test_should_return_data_of_form_by_form_code(self):
        dbm = Mock(spec=DatabaseManager)
        with patch.object(dbm, "load_all_rows_in_view") as load_all_rows_in_view:
            load_all_rows_in_view.return_value =  [{"id": "1", "key": [["clinic"], "cid001", 1],
                                                    "value": {"What is the GPS code for clinic?": [79.2, 20.34567]}},
                    {"id": "1", "key": [["clinic"], "cid001", 1],
                     "value": {"What is the GPS code for clinic?": [79.2, 20.34567]}}]
            form_data = get_data_for_form(dbm, "cli")
            self.assertTrue(isinstance(form_data, list))
            self.assertEqual(2, len(form_data))

    def test_should_return_data_with_success_status_and_value_for_form(self):
        dbm = Mock()
        with patch("dataextraction.helper.get_data_for_form") as get_data_for_form:
            get_data_for_form.return_value = [ {"What is the GPS code for clinic?": [79.2, 20.34567]},
                    {"What is the GPS code for clinic?": [79.2, 20.34567]}]
            data_for_form = encapsulate_data_for_form(dbm, "cli")
            self.assertIsInstance(data_for_form, DataExtractionResult)
            self.assertTrue(data_for_form.success)
            self.assertEqual(2, len(data_for_form.value))

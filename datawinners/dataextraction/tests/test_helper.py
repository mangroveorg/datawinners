from unittest.case import TestCase
from mangrove.datastore.database import DatabaseManager
from mock import Mock
from mock import patch
from datawinners.dataextraction.models import DataExtractionResult
from datawinners.dataextraction.helper import get_data_for_form, encapsulate_data_for_form, generate_filename

DATA_FROM_DB = [{"id": "1", "key": [["clinic"], "cid001", 1],
                 "value": {"submission_time": "2012-08-08 03:21:23.469462+00:00",
                           "submission_data": {"What is the GPS code for clinic?": [79.2, 20.34567]}}},
        {"id": "1", "key": [["clinic"], "cid001", 1], "value": {"submission_time": "2012-08-07 03:21:23.469462+00:00",
                                                                "submission_data": {
                                                                    "What is the GPS code for clinic?": [79.2,
                                                                                                         20.34567]}}}]

TRANSFORMED_DATA = [{"submission_time": "2012-08-08 03:21:23.469462+00:00",
                     "submission_data": {"What is the GPS code for clinic?": [79.2, 20.34567]}},
        {"submission_time": "2012-08-07 03:21:23.469462+00:00",
         "submission_data": {
             "What is the GPS code for clinic?": [79.2,
                                                  20.34567]}}]

class TestHelper(TestCase):

    def test_should_return_data_of_form_by_form_code(self):
        dbm = Mock(spec=DatabaseManager)
        with patch("datawinners.dataextraction.helper.check_if_form_exists") as check_if_form_exists:
            check_if_form_exists.return_value = True
            with patch.object(dbm, "load_all_rows_in_view") as load_all_rows_in_view:
                load_all_rows_in_view.return_value = DATA_FROM_DB
                form_data = get_data_for_form(dbm, "cli")
                self.assertTrue(isinstance(form_data, list))
                self.assertEqual(2, len(form_data))

    def test_should_return_data_with_success_status_and_value_for_form(self):
        dbm = Mock()
        with patch("datawinners.dataextraction.helper.check_if_form_exists") as check_if_form_exists:
            check_if_form_exists.return_value = True
            with patch("datawinners.dataextraction.helper.get_data_for_form") as get_data_for_form:
                get_data_for_form.return_value = TRANSFORMED_DATA
                data_for_form = encapsulate_data_for_form(dbm, "cli")
                self.assertIsInstance(data_for_form, DataExtractionResult)
                self.assertTrue(data_for_form.success)
                self.assertEqual(2, len(data_for_form.submissions))

    def test_should_return_data_with_failed_status_for_form_when_pass_not_exist_form_code(self):
        dbm = Mock()
        with patch("datawinners.dataextraction.helper.check_if_form_exists") as check_if_form_exists:
            check_if_form_exists.return_value = False
            not_exist_form_code = "cli"
            data_for_form = encapsulate_data_for_form(dbm, not_exist_form_code)
            self.assertIsInstance(data_for_form, DataExtractionResult)
            self.assertFalse(data_for_form.success)
            self.assertEqual(0, len(data_for_form.submissions))
            self.assertEqual(data_for_form.message, "Questionnaire code [%s] does not existed." % not_exist_form_code)

    def test_should_return_data_with_failed_status_for_form_when_pass_wrong_date_format(self):
        dbm = Mock()
        with patch("datawinners.dataextraction.helper.check_if_form_exists") as check_if_form_exists:
            check_if_form_exists.return_value = True
            data_for_form = encapsulate_data_for_form(dbm, "cli", "03082012", "06082012")
            self.assertIsInstance(data_for_form, DataExtractionResult)
            self.assertFalse(data_for_form.success)
            self.assertEqual(0, len(data_for_form.submissions))
            self.assertEqual(data_for_form.message, "The format of start and end date should be DD-MM-YYYY. Example: 25-12-2011")

    def test_should_return_data_with_failed_status_for_form_when_end_date_before_start_date(self):
        dbm = Mock()
        with patch("datawinners.dataextraction.helper.check_if_form_exists") as check_if_form_exists:
            check_if_form_exists.return_value = True
            data_for_form = encapsulate_data_for_form(dbm, "cli", "09-08-2012", "03-08-2012")
            self.assertIsInstance(data_for_form, DataExtractionResult)
            self.assertFalse(data_for_form.success)
            self.assertEqual(0, len(data_for_form.submissions))
            self.assertEqual(data_for_form.message, "Start date must before end date.")

    def test_should_return_data_with_success_status_and_no_data_message_for_form_when_no_data(self):
        dbm = Mock()
        with patch("datawinners.dataextraction.helper.check_if_form_exists") as check_if_form_exists:
            check_if_form_exists.return_value = True
            with patch("datawinners.dataextraction.helper.get_data_for_form") as get_data_for_form:
                get_data_for_form.return_value = []
                data_for_form = encapsulate_data_for_form(dbm, "cli", "01-08-2012", "03-08-2012")
                self.assertIsInstance(data_for_form, DataExtractionResult)
                self.assertTrue(data_for_form.success)
                self.assertEqual(0, len(data_for_form.submissions))
                self.assertEqual("No submission under this questionnaire during this period.", data_for_form.message)

    def test_should_return_download_filename_which_only_contains_main_filename_when_not_pass_date(self):
        main = "main_filename"
        filename = generate_filename(main)
        self.assertEqual(filename, main)

    def test_should_return_download_filename_which_ends_with_start_date_when_pass_start_date(self):
        main = "main_filename"
        start_date = '06-08-2012'
        filename = generate_filename(main, start_date)
        self.assertEqual(filename, "%s_%s" % (main, start_date))

    def test_should_return_download_filename_which_ends_with_start_and_end_date_when_pass_both_start_and_end_date(self):
        main = "main_filename"
        start_date = '06-08-2012'
        end_date = '08-08-2012'
        filename = generate_filename(main, start_date, end_date)
        self.assertEqual(filename, "%s_%s_%s" % (main, start_date, end_date))

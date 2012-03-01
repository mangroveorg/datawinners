# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from collections import OrderedDict
import unittest
from mangrove.transport.player.tests.test_web_player import mock_form_submission
from mock import Mock, patch
from datawinners.entity.import_data import FilePlayer
from mangrove.datastore.database import DatabaseManager
from mangrove.errors.MangroveException import FormModelDoesNotExistsException
from mangrove.form_model.form_model import FormModel, FormSubmission, FormSubmissionFactory
from mangrove.transport.player.parser import CsvParser
from mangrove.transport import Channel


class TestCsvPlayer(unittest.TestCase):

    def _mock_form_model(self):
        self.get_form_model_mock_patcher = patch('datawinners.entity.import_data.get_form_model_by_code')
        get_form_model_mock = self.get_form_model_mock_patcher.start()
        self.form_model_mock = Mock(spec=FormModel)
        get_form_model_mock.return_value = self.form_model_mock
        self.form_model_mock.is_registration_form = Mock(return_value=False)
        self.form_model_mock.entity_defaults_to_reporter = Mock(return_value=False)
        self.form_model_mock.is_inactive.return_value = False
        self.form_model_mock.validate_submission.return_value = OrderedDict(), OrderedDict()

        self.form_submission_mock = mock_form_submission(self.form_model_mock)

    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        loc_tree = Mock()
        loc_tree.get_hierarchy_path.return_value = None
        self.parser = CsvParser()

        self.csv_data = """
                                FORM_CODE,ID,BEDS,DIRECTOR,MEDS
                                CLF1,CL001,10,Dr. A,201
                                CLF1,CL002,11,Dr. B,202
                                CLF2,CL003,12,Dr. C,203
                                CLF1,CL004,13,Dr. D,204
                                CLF1,CL005,14,Dr. E,205
"""
        self._mock_form_model()
        self.player = FilePlayer(self.dbm, self.parser, Channel.CSV, loc_tree)

    def tearDown(self):
        self.get_form_model_mock_patcher.stop()

    def test_should_import_csv_string(self):
        with patch.object(FormSubmissionFactory, 'get_form_submission') as get_form_submission_mock:
            get_form_submission_mock.return_value = self.form_submission_mock
            self.player.accept(self.csv_data)
            self.assertEqual(5, self.form_model_mock.validate_submission.call_count)

    def test_should_process_next_submission_if_exception_with_prev(self):
        def expected_side_effect(*args, **kwargs):
            values = kwargs.get('values') or args[1]
            if values.get('id') == 'CL003':
                raise FormModelDoesNotExistsException('')
            return values, OrderedDict()

        self.form_model_mock.validate_submission.side_effect = expected_side_effect

        with patch.object(FormSubmissionFactory, 'get_form_submission') as get_form_submission_mock:
            get_form_submission_mock.return_value = self.form_submission_mock

            response = self.player.accept(self.csv_data)
            self.assertEqual(5, len(response))
            self.assertEqual(False, response[2].success)

            success = len([index for index in response if index.success])
            total = len(response)
            self.assertEqual(4, success)
            self.assertEqual(5, total)

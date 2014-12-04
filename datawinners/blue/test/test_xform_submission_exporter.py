from collections import OrderedDict
import unittest
from mock import MagicMock
from nose.plugins.attrib import attr
from datawinners.blue.xform_submission_exporter import AdvanceSubmissionFormatter
from mangrove.form_model.form_model import FormModel


class TestXFormSubmissionExporter(unittest.TestCase):

    def test_should_tabulate_header_and_submissions_rows(self):
        form_model_mock = MagicMock(spec=FormModel)
        family_dict = OrderedDict({'name': {'type': 'text', 'label': 'Name'}})
        family_dict.update({'age': {'type': 'text', 'label': 'Age'}})

        columns = OrderedDict([('ds_id', {'label': 'Datasender Id'}),
                               ('uuid1_family',
                                {'fields': family_dict, 'type': 'field_set', 'label': 'Family','fieldset_type':'repeat'}),
                               ('uuid1_city', {'type': 'text', 'label': 'City'}),
                               ('area', {'type': 'text', 'label': 'Area'})])
        # correct the question to represent correct hierarchy
        submission_list = [{"_source":{'uuid1_family': '[{"name": "ram", "age":"20"}, {"name": "shyam", "age":"25"}]',
                            'ds_id': 'rep276', 'uuid1_city': 'Pune', 'area': '500'}},
            {"_source":{'uuid1_family': '[{"name": "maya", "age":"20"}, {"name": "rita", "age":"25"}]',
                            'ds_id': 'rep277', 'uuid1_city': 'Bangalore', 'area': '800'}}]

        expected_header = ['Datasender Id', 'City', 'Area','_index', '_parent_index']
        expected_family_header = ['Name', 'Age', '_index', '_parent_index']

        main_submission_rows = [['rep276', 'Pune', '500', 1],
                                ['rep277', 'Bangalore', '800', 2]]
        repeat_family_rows = [['ram', '20', '', 1], ['shyam', '25', '', 1], ['maya', '20', '', 2],
                              ['rita', '25', '', 2]]

        headers, data_rows_dict = AdvanceSubmissionFormatter(columns, form_model_mock, ('+', 0, 0)).format_tabular_data(submission_list)

        self.assertEqual(expected_header, headers['main'])
        self.assertEqual(expected_family_header, headers['family'])

        self.assertEqual(main_submission_rows, data_rows_dict['main'])
        self.assertEqual(repeat_family_rows, data_rows_dict['family'])

    def test_should_tabulate_header_and_submissions_rows_for_select_field(self):
        form_model_mock = MagicMock(spec=FormModel)

        columns = OrderedDict([('uuid1_city', {'type': 'select', 'label': 'City'})])
        submission_list = [{"_source":{'uuid1_city': ['Bangalore','Pune']}}]

        expected_header = ['City','_index', '_parent_index']
        main_submission_rows = [['Bangalore; Pune',1]]
        headers, data_rows_dict = AdvanceSubmissionFormatter(columns, form_model_mock, ('+', 0, 0)).format_tabular_data(submission_list)

        self.assertEqual(expected_header, headers['main'])
        self.assertEqual(main_submission_rows, data_rows_dict['main'])

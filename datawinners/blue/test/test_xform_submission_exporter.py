from collections import OrderedDict
import unittest
from mock import MagicMock
from datawinners.blue.xform_submission_exporter import AdvanceSubmissionFormatter, \
    AdvancedQuestionnaireSubmissionExportHeaderCreator
from mangrove.form_model.form_model import FormModel


class TestAdvancedQuestionnaireSubmissionExporter(unittest.TestCase):

    def test_should_create_headers_(self):
        form_model_mock = MagicMock(spec=FormModel)
        family_dict = OrderedDict({'name': {'type': 'text', 'label': 'Name'}})
        family_dict.update({'age': {'type': 'text', 'label': 'Age'}})

        columns = OrderedDict([('ds_id', {'label': 'Datasender Id'}),
                               ('uuid1_family',
                                {'fields': family_dict, 'type': 'field_set', 'label': 'Family','fieldset_type':'repeat'}),
                               ('uuid1_city', {'type': 'text', 'label': 'City'}),
                               ('area', {'type': 'text', 'label': 'Area'})])

        expected_header = ['Datasender Id', 'City', 'Area','_index', '_parent_index']
        expected_family_header = ['Name', 'Age', '_index', '_parent_index']

        headers = AdvancedQuestionnaireSubmissionExportHeaderCreator(columns, form_model_mock).create_headers()

        self.assertEqual(expected_header, headers['main'])
        self.assertEqual(expected_family_header, headers['family'])

    def test_should_create_header_select_field(self):
        form_model_mock = MagicMock(spec=FormModel)

        columns = OrderedDict([('uuid1_city', {'type': 'select', 'label': 'City'})])

        expected_header = ['City','_index', '_parent_index']

        headers = AdvancedQuestionnaireSubmissionExportHeaderCreator(columns, form_model_mock).create_headers()

        self.assertEqual(expected_header, headers['main'])
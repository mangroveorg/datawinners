from collections import OrderedDict
import unittest
from mock import MagicMock
from datawinners.blue.xform_submission_exporter import AdvanceSubmissionFormatter, \
    AdvancedQuestionnaireSubmissionExportHeaderCreator, AdvancedQuestionnaireSubmissionExporter
from mangrove.form_model.form_model import FormModel


class TestAdvancedQuestionnaireSubmissionExporter(unittest.TestCase):

    def test_should_create_headers_(self):
        form_model_mock = MagicMock(spec=FormModel)
        family_dict = OrderedDict({'name': {'type': 'text', 'label': 'Name'}})
        family_dict.update({'age': {'type': 'text', 'label': 'Age'}})

        columns = OrderedDict([('ds_id', {'label': 'Data Sender Id'}),
                               ('uuid1_family',
                                {'fields': family_dict, 'type': 'field_set', 'code': 'field_code', 'label': 'Family','fieldset_type':'repeat'}),
                               ('uuid1_city', {'type': 'text', 'label': 'City'}),
                               ('area', {'type': 'text', 'label': 'Area'})])

        expected_header = ['Data Sender Id', 'City', 'Area','_index', '_parent_index']
        expected_family_header = ['Name', 'Age', '_index', '_parent_index']
        preferences = [dict(data='ds_id', visibility='True'),
                       dict(data='uuid1_family', visibility='True', children=[dict(data='name',visibility='True'),
                                                                              dict(data='age',visibility='True')]),
                       dict(data='uuid1_city',visibility=False), dict(data='area',visibility='True')]

        headers = AdvancedQuestionnaireSubmissionExportHeaderCreator(columns, form_model_mock, preferences).create_headers()

        self.assertEqual(expected_header, headers['main'])
        self.assertEqual(expected_family_header, headers['field_code'])

    def test_should_create_header_select_field(self):
        form_model_mock = MagicMock(spec=FormModel)

        columns = OrderedDict([('uuid1_city', {'type': 'select', 'label': 'City'})])

        expected_header = ['City','_index', '_parent_index']

        preferences = OrderedDict()

        headers = AdvancedQuestionnaireSubmissionExportHeaderCreator(columns, form_model_mock, preferences).create_headers()

        self.assertEqual(expected_header, headers['main'])


    def test_should_create_header_geocode_field(self):
        form_model_mock = MagicMock(spec=FormModel)

        columns = OrderedDict([('uuid1_city', {'type': 'geocode', 'label': 'G P S Coordinates'})])

        expected_header = ['G P S Coordinates Latitude', 'G P S Coordinates Longitude','_index', '_parent_index']

        local_time_delta = '+', 0, 0

        preferences = [dict(data='uuid1_city',visibility=True), dict(data='area',visibility=False)]

        headers = AdvancedQuestionnaireSubmissionExporter(form_model_mock, columns, local_time_delta, preferences).\
            get_visible_headers()

        self.assertEqual(expected_header, headers['main'])

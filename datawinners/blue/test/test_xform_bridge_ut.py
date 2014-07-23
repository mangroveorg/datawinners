import unittest
from mock import patch
from datawinners.blue.xform_bridge import XlsFormParser, UppercaseNamesNotSupportedException, \
    NestedRepeatsNotSupportedException


class TestXformBridgeUt(unittest.TestCase):

    def test_xform_validation_for_uppercase_names(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            xls_form_parser = XlsFormParser('some_path')
            fields = {
            'children': [{u'bind': {u'required': u'yes'}, u'type': u'text', u'name': u'name', u'label': u'Name'}, {
                u'children': [
                    {u'bind': {u'required': u'no'}, u'type': u'text', u'name': u'college', u'label': u'College Name'}
                ],
                # here is uppercase name
                u'type': u'repeat', u'name': u'Highest_Degree', u'label': u'degree'},
                {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                             {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                              'type': 'calculate',
                              'name': 'instanceID'}]}]}

            get_xform_dict.return_value = fields
            self.assertRaises(UppercaseNamesNotSupportedException, xls_form_parser._validate_fields_are_recognised,
                              fields['children'])

    def test_xform_validation_for_nested_repeats_names(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            xls_form_parser = XlsFormParser('some_path')
            fields = {'children':[{u'bind': {u'required': u'yes'}, u'type': u'text', u'name': u'name', u'label': u'Name'},
                 {u'children': [{u'children': [
                     {u'bind': {u'required': u'no'}, u'type': u'text', u'name': u'college', u'label': u'College Name'}],
                                 u'type': u'repeat', u'name': u'some', u'label': u'some'}], u'type': u'repeat',
                  u'name': u'Highest_Degree', u'label': u'degree'},
                 {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                     {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"}, 'type': 'calculate',
                      'name': 'instanceID'}]}]}
            get_xform_dict.return_value = fields
            self.assertRaises(NestedRepeatsNotSupportedException, xls_form_parser._validate_fields_are_recognised,
                              fields['children'])
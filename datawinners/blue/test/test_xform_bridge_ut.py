import os
import unittest
from couchdb.client import Row

from mock import patch, Mock

from datawinners.blue.xform_bridge import XlsFormParser, get_generated_xform_id_name, \
    _map_unique_id_question_to_select_one
from mangrove.datastore.database import View, DatabaseManager


DIR = os.path.dirname(__file__)


class TestXformBridge(unittest.TestCase):
    def test_xform_validation_for_nested_repeats_names(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')
            fields = {
                'children': [{u'bind': {u'required': u'yes'}, u'type': u'text', u'name': u'name', u'label': u'Name'},
                             {u'children': [{u'children': [
                                 {u'bind': {u'required': u'no'}, u'type': u'text', u'name': u'college',
                                  u'label': u'College Name'}],
                                             u'type': u'repeat', u'name': u'some', u'label': u'some'}],
                              u'type': u'repeat',
                              u'name': u'highest_degree', u'label': u'degree'},
                             {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                 {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                  'type': 'calculate',
                                  'name': 'instanceID'}]}]}
            get_xform_dict.return_value = fields
            actual_errors = xls_form_parser._validate_fields_are_recognised(fields['children'])

            self.assertEqual(actual_errors, {"more than one level of repeated questions."})


    def test_should_populate_error_when_label_defined_in_multiple_languages(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')
            fields = {'children': [{u'bind': {u'required': u'yes'}, u'type': u'text', u'name': u'name',
                                    u'label': {u'french': u'1. What is your name?',
                                               u'english': u'1. What is your name?'}},
                                   {u'bind': {u'required': u'yes'}, u'type': u'integer', u'name': u'age',
                                    u'label': {u'french': u'2. What is your age?',
                                               u'english': u'2. What is your age?'}},
                                   {u'bind': {u'required': u'yes'}, u'type': u'text', u'name': u'new_loc',
                                    u'label': {u'french': u'1. What is your new loc?',
                                               u'english': u'1. What is your new loc?'}},
                                   {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                       {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                        'type': 'calculate', 'name': 'instanceID'}]}]}
            get_xform_dict.return_value = fields
            actual_errors = xls_form_parser._validate_fields_are_recognised(fields['children'])
            self.assertEquals(actual_errors, {"XLSForm language settings."})

    def test_should_populate_error_when_label_defined_in_single_explict_language(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')
            fields = {'children': [{u'bind': {u'required': u'yes'}, u'type': u'text', u'name': u'name',
                                    u'label': {u'english': u'1. What is your name?'}},
                                   {u'bind': {u'required': u'yes'}, u'type': u'integer', u'name': u'age',
                                    u'label': {u'english': u'2. What is your age?'}},
                                   {u'bind': {u'required': u'yes'}, u'type': u'text', u'name': u'new_loc',
                                    u'label': {u'english': u'1. What is your new loc?'}},
                                   {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                       {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                        'type': 'calculate', 'name': 'instanceID'}]}]}
            get_xform_dict.return_value = fields
            actual_errors = xls_form_parser._validate_fields_are_recognised(fields['children'])
            self.assertEquals(actual_errors, {"XLSForm language settings."})

    def test_should_populate_error_when_hint_defined_in_one_or_more_languages(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')
            fields = {'children': [{u'bind': {u'required': u'yes'}, u'type': u'text', u'name': u'name',
                                    u'label': u'1. What is your name?', u'hint': {u'hindi': u'Hindi hint'}},
                                   {u'bind': {u'required': u'yes'}, u'type': u'integer', u'name': u'age',
                                    u'label': u'2. What is your age?', u'hint': {u'hindi': u'Hindi hint'}},
                                   {u'bind': {u'required': u'yes'}, u'type': u'text', u'name': u'new_loc',
                                    u'label': u'1. What is your new loc?', u'hint': {u'hindi': u'Hindi hint'}},
                                   {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                       {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                        'type': 'calculate', 'name': 'instanceID'}]}]}
            get_xform_dict.return_value = fields

            actual_errors = xls_form_parser._validate_fields_are_recognised(fields['children'])

            self.assertEquals(actual_errors, {"XLSForm language settings."})

    def test_should_populate_error_when_the_label_in_choice_sheets_has_language(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')
            fields = {'children': [{u'bind': {u'required': u'yes'}, u'type': u'text', u'name': u'name',
                                    u'label': u'1. What is your name?'},
                                   {u'bind': {u'required': u'yes'}, u'type': u'integer', u'name': u'age',
                                    u'label': u'2. What is your age?'},
                                   {u'bind': {u'required': u'yes'}, u'type': u'select one', u'name': u'is_student',
                                    u'label': u'1. Are you a student?',
                                    u'choices': [{u'name': u'yes', u'label': {u'hindi': u'Yes'}},
                                                 {u'name': u'no', u'label': {u'hindi': u'No'}}]},
                                   {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                       {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                        'type': 'calculate', 'name': 'instanceID'}]}]}
            get_xform_dict.return_value = fields
            actual_errors = xls_form_parser._validate_fields_are_recognised(fields['children'])
            self.assertEquals(actual_errors, {"XLSForm language settings."})


    def test_should_populate_error_when_choice_has_no_label(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {'children': [{u'bind': {u'required': u'yes'}, u'type': u'select one', u'name': u'is_student',
                                    u'label': u'1. Are you a student?',
                                    u'choices': [{u'name': u'yes'}, {u'name': u'no', u'label': u'No'}]},
                                   {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                       {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                        'type': 'calculate', 'name': 'instanceID'}]}],
                      'title': 'asdasx',
                      'name': 'asdasx',
                      'id_string': 'asdasx',
                      'default_language': 'default'
            }
            get_xform_dict.return_value = fields
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')

            xls_parser_response = xls_form_parser.parse()

            self.assertEquals(xls_parser_response.errors,
                              {"optional labels. Label is a mandatory field for choice option with name [yes]"})

    def test_should_populate_error_when_choice_name_has_spaces_and_unique_name(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {'children': [{u'bind': {u'required': u'yes'}, u'type': u'select one', u'name': u'is_student',
                                    u'label': u'1. Are you a student?',
                                    u'choices': [{u'name': u'yes 1', u'label': 'yes'},
                                                 {u'name': u'yes 1', u'label': u'No'}]},
                                   {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                       {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                        'type': 'calculate', 'name': 'instanceID'}]}],
                      'title': 'asdasx',
                      'name': 'asdasx',
                      'id_string': 'asdasx',
                      'default_language': 'default'
            }
            get_xform_dict.return_value = fields
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')

            xls_parser_response = xls_form_parser.parse()

            self.assertEquals(xls_parser_response.errors, {"duplicate names within one list (choices sheet)",
                                              "spaces in name column (choice sheet)"})

    def test_should_populate_error_when_calculate_field_with_prefetch_present(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {'children': [
                {u'bind': {u'calculate': u'pulldata(fruit, "mangoes")'}, u'type': u'calculate', u'name': u'calc',
                 u'label': u'1. Are you a student?'},
                {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                    {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                     'type': 'calculate', 'name': 'instanceID'}]}],
                      'title': 'asdasx',
                      'name': 'asdasx',
                      'id_string': 'asdasx',
                      'default_language': 'default'
            }
            get_xform_dict.return_value = fields
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')

            xls_parser_response = xls_form_parser.parse()

            self.assertEquals(xls_parser_response.errors, {"preloading of CSV data (the PullData() function)."})

    def test_should_populate_error_when_settings_sheet_present_with_form_title(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {'children': [{u'bind': {u'required': u'no'}, u'type': u'text', u'name': u'college',
                                    u'label': u'College Name'},
                                   {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                       {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                        'type': 'calculate', 'name': 'instanceID'}]}],
                      'title': 'My form title',
                      'name': 'asdasx',
                      'id_string': 'asdasx',
                      'default_language': 'default'
            }
            get_xform_dict.return_value = fields
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')

            xls_parser_response = xls_form_parser.parse()

            self.assertEquals(xls_parser_response.errors, {"XLSForm settings worksheet and the related values in survey sheet."})


    def test_should_populate_error_when_settings_sheet_present_with_form_id(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {'children': [{u'bind': {u'required': u'no'}, u'type': u'text', u'name': u'college',
                                    u'label': u'College Name'},
                                   {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                       {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                        'type': 'calculate', 'name': 'instanceID'}]}],
                      'title': 'asdasx',
                      'name': 'asdasx',
                      'id_string': 'My Form Id',
                      'default_language': 'default'
            }
            get_xform_dict.return_value = fields
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')

            xls_parser_response = xls_form_parser.parse()

            self.assertEquals(xls_parser_response.errors, {"XLSForm settings worksheet and the related values in survey sheet."})

    def test_should_populate_error_when_settings_sheet_present_with_public_key(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {'children': [{u'bind': {u'required': u'no'}, u'type': u'text', u'name': u'college',
                                    u'label': u'College Name'},
                                   {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                       {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                        'type': 'calculate', 'name': 'instanceID'}]}],
                      'title': 'asdasx',
                      'name': 'asdasx',
                      'id_string': 'asdasx',
                      'public_key': 'my_public_key',
                      'default_language': 'default'
            }
            get_xform_dict.return_value = fields
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')

            xls_parser_response = xls_form_parser.parse()

            self.assertEquals(xls_parser_response.errors, {"XLSForm settings worksheet and the related values in survey sheet."})

    def test_should_populate_error_when_settings_sheet_present_with_default_language(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {'children': [{u'bind': {u'required': u'no'}, u'type': u'text', u'name': u'college',
                                    u'label': u'College Name'},
                                   {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                       {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                        'type': 'calculate', 'name': 'instanceID'}]}],
                      'title': 'asdasx',
                      'name': 'asdasx',
                      'id_string': 'asdasx',
                      'default_language': 'default_something'
            }
            get_xform_dict.return_value = fields
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')

            xls_parser_response = xls_form_parser.parse()

            self.assertEquals(xls_parser_response.errors, {"XLSForm settings worksheet and the related values in survey sheet."})

    def test_should_populate_error_when_settings_sheet_present_with_submission_url(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {'children': [{u'bind': {u'required': u'no'}, u'type': u'text', u'name': u'college',
                                    u'label': u'College Name'},
                                   {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                       {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                        'type': 'calculate', 'name': 'instanceID'}]}],
                      'title': 'asdasx',
                      'name': 'asdasx',
                      'id_string': 'asdasx',
                      'submission_url': 'my submission url',
                      'default_language': 'default'
            }
            get_xform_dict.return_value = fields
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')

            xls_parser_response = xls_form_parser.parse()

            self.assertEquals(xls_parser_response.errors, {"XLSForm settings worksheet and the related values in survey sheet."})

    def test_should_not_create_question_for_select_that_are_only_labels(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')
            fields = [{u'control': {u'appearance': u'label'}, u'name': u'table_list_test_label',
                       u'hint': u'Show only the labels of these options and not the inputs (type=select_one yes_no, appearance=label)',
                       u'choices': [{u'name': u'yes', u'label': u'Yes'}, {u'name': u'no', u'label': u'No'},
                                    {u'name': u'dk', u'label': u"Don't Know"},
                                    {u'name': u'na', u'label': u'Not Applicable'}], u'label': u'Table',
                       u'type': u'select one'}, {u'control': {u'appearance': u'list-nolabel'}, u'name': u'table_list_1',
                                                 u'hint': u'Show only the inputs of these options and not the labels (type=select_one yes_no, appearance=list-nolabel)',
                                                 u'choices': [{u'name': u'yes', u'label': u'Yes'},
                                                              {u'name': u'no', u'label': u'No'},
                                                              {u'name': u'dk', u'label': u"Don't Know"},
                                                              {u'name': u'na', u'label': u'Not Applicable'}],
                                                 u'label': u'Q1', u'type': u'select one'},
                      {u'control': {u'appearance': u'list-nolabel'}, u'name': u'table_list_2',
                       u'hint': u'Show only the inputs of these options and not the labels (type=select_one yes_no, appearance=list-nolabel)',
                       u'choices': [{u'name': u'yes', u'label': u'Yes'}, {u'name': u'no', u'label': u'No'},
                                    {u'name': u'dk', u'label': u"Don't Know"},
                                    {u'name': u'na', u'label': u'Not Applicable'}], u'label': u'Question 2',
                       u'type': u'select one'}, {'control': {'bodyless': True}}]

            questions, errors, unique_id_errors = xls_form_parser._create_questions(fields)

            self.assertEqual(questions.__len__(), 2)
            self.assertDictEqual(questions[0], {'code': u'table_list_1', 'title': u'Q1', 'required': False,
                                                'parent_field_code': None,
                                                'has_other': False,
                                                'choices': [{'value': {'text': u'Yes', 'val': u'yes'}},
                                                            {'value': {'text': u'No', 'val': u'no'}},
                                                            {'value': {'text': u"Don't Know", 'val': u'dk'}},
                                                            {'value': {'text': u'Not Applicable', 'val': u'na'}}],
                                                'is_entity_question': False, 'type': 'select1'})
            self.assertDictEqual(questions[1], {'code': u'table_list_2', 'title': u'Question 2', 'required': False,
                                                'parent_field_code': None,
                                                'has_other': False,
                                                'choices': [{'value': {'text': u'Yes', 'val': u'yes'}},
                                                            {'value': {'text': u'No', 'val': u'no'}},
                                                            {'value': {'text': u"Don't Know", 'val': u'dk'}},
                                                            {'value': {'text': u'Not Applicable', 'val': u'na'}}],
                                                'is_entity_question': False, 'type': 'select1'})

    def test_should_create_additional_text_question_for_single_select_or_other_question(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')
            fields = [{u'choices': [{u'name': u'male', u'label': u'Male'}, {u'name': u'female', u'label': u'Female'}],
                       u'type': u'select one or specify other', u'name': u'hh_user_gender', u'label': u'Sex'},
                      {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                          {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"}, 'type': 'calculate',
                           'name': 'instanceID'}]}]

            questions, errors, unique_id_errors = xls_form_parser._create_questions(fields)

            self.assertEqual(questions.__len__(), 2)
            self.assertDictEqual(questions[0], {'code': u'hh_user_gender', 'title': u'Sex', 'required': False,
                                                'parent_field_code': None,
                                                'has_other': True,
                                                'choices': [{'value': {'text': u'Male', 'val': u'male'}},
                                                            {'value': {'text': u'Female', 'val': u'female'}}],
                                                'is_entity_question': False, 'type': 'select1'})
            self.assertDictEqual(questions[1], {'code': u'hh_user_gender_other', 'title': u'Sex_other', 'required': False,
                                                'parent_field_code': None,
                                                'name': u'Sex_other',
                                                'instruction': 'Answer must be a word',
                                                'is_entity_question': False, 'type': u'text'})


    def test_should_return_correct_date_format_for_year_or_monthyear_appearance(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {'children': [
                {u'type': u'date', u'name': u'birth_date', u'label': u'1. What is your date of birth?',
                 u'control': {u'appearance': u'year'}},
                {u'type': u'date', u'name': u'birth_date2', u'label': u'2. What is your date of birth?',
                 u'control': {u'appearance': u'month-year'}}]}
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')
            self.assertEquals('yyyy', xls_form_parser._get_date_format(fields['children'][0]))
            self.assertEquals('mm.yyyy', xls_form_parser._get_date_format(fields['children'][1]))

    def test_should_return_correct_date_format_for_year_or_monthyear_appearance_combined_With_other_appearance(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {'children': [
                {u'type': u'date', u'name': u'birth_date', u'label': u'1. What is your date of birth?',
                 u'control': {u'appearance': u'w2 year'}},
                {u'type': u'date', u'name': u'birth_date2', u'label': u'2. What is your date of birth?',
                 u'control': {u'appearance': u'w4 horizontal month-year'}}]}
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')
            self.assertEquals('yyyy', xls_form_parser._get_date_format(fields['children'][0]))
            self.assertEquals('mm.yyyy', xls_form_parser._get_date_format(fields['children'][1]))

    def test_should_return_default_date_format_for_any_other_appearance(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {'children': [
                {u'type': u'date', u'name': u'birth_date', u'label': u'1. What is your date of birth?',
                 u'control': {u'appearance': u'w4'}
                }]}
            get_xform_dict.return_value = fields

            get_xform_dict.return_value = fields
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')
            self.assertEquals('dd.mm.yyyy', xls_form_parser._get_date_format(fields['children'][0]))

    def test_should_populate_error_when_unsupported_geoshape_question_present_within_a_repeat(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {u'children': [
                {u'children': [
                    {u'bind': {u'required': u'yes'},
                     u'type': u'geoshape', u'name': u'timeq', u'label': u'Time q'},
                    {u'bind': {u'required': u'yes'}, u'type': u'datetime', u'name': u'datetq',
                     u'label': u'Date time q'}],
                 u'type': u'group', u'name': u'mygroup', u'label': u'My group'
                }], u'type': u'repeat', u'name': u'myrepeat', u'label': u'My repeat',
                      'title': 'asdasx',
                      'name': 'asdasx',
                      'id_string': 'asdasx',
                      'default_language': 'default'
            }

            get_xform_dict.return_value = fields
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')

            xls_parser_response = xls_form_parser.parse()

            self.assertEquals(xls_parser_response.errors, {"geoshape as a datatype"})

    def test_should_populate_error_when_media_type_present_as_a_data_type(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {u'children': [{u'name': u'bird', u'hint': u'Some birds have included images or audio.',
                                     u'media': {u'audio': u'question.wav'},
                                     u'choices': [{u'name': u'eagle', u'label': u'Eagle'}],
                                     u'label': u'What bird did you see?', u'type': u'select one'},
                                    {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                        {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                         'type': 'calculate', 'name': 'instanceID'}]}], u'type': u'repeat',
                      u'name': u'myrepeat', u'label': u'My repeat',
                      'title': 'asdasx',
                      'name': 'asdasx',
                      'id_string': 'asdasx',
                      'default_language': 'default'
            }

            get_xform_dict.return_value = fields
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')

            xls_parser_response = xls_form_parser.parse()

            self.assertEquals(xls_parser_response.errors, {"XLSForm media type (audio) in survey sheet."})


    def test_should_populate_error_when_choice_answer_has_media_present(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {u'children': [{u'choices': [{u'name': u'crow', u'label': u'crow'},
                                                  {u'media': {u'image': u'eagle.png'}, u'name': u'eagle',
                                                   u'label': u'Eagle'}], u'label': u'What bird did you see?',
                                     u'type': u'select one', u'name': u'bird',
                                     u'hint': u'Some birds have included images or audio.'},
                                    {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                                        {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"},
                                         'type': 'calculate', 'name': 'instanceID'}]}], u'type': u'repeat',
                      u'name': u'myrepeat', u'label': u'My repeat',
                      'title': 'asdasx',
                      'name': 'asdasx',
                      'id_string': 'asdasx',
                      'default_language': 'default'
            }

            get_xform_dict.return_value = fields
            xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')

            xls_parser_response = xls_form_parser.parse()

            self.assertEquals(xls_parser_response.errors, {"XLSForm media type (image) in choices sheet."})


    def test_should_not_populate_errors_when_choice_answer_has_no_media_present(self):
        with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
            fields = {u'name': u'tmpGX1Ud_', u'title': u'tmpGX1Ud_', u'sms_keyword': u'tmpGX1Ud_',
                      u'default_language': u'default', u'id_string': u'tmpGX1Ud_', u'type': u'survey', u'children': [
                {u'choices': [{u'name': u'crow', u'label': u'crow'}, {u'name': u'eagle', u'label': u'Eagle'}],
                 u'label': u'What bird did you see?', u'type': u'select one', u'name': u'bird',
                 u'hint': u'Some birds have included images or audio.'},
                {'control': {'bodyless': True}, 'type': 'group', 'name': 'meta', 'children': [
                    {'bind': {'readonly': 'true()', 'calculate': "concat('uuid:', uuid())"}, 'type': 'calculate',
                     'name': 'instanceID'}]}]}
            get_xform_dict.return_value = fields
            xls_form_parser = XlsFormParser('some_path', u'questionnaire_name')

            xls_parser_response = xls_form_parser.parse()

            self.assertEquals(xls_parser_response.errors, [])

    def test_should_create_entity_question_for_dw_idnr_question(self):
        with patch('datawinners.blue.xform_bridge.entity_type_already_defined') as is_entity_type_already_defined:
            with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
                manager = Mock(DatabaseManager)
                manager.view = Mock(View)
                manager.view.count_non_voided_entities_by_type = Mock(return_value=[Row({'key':['clinic'],'value':10})])
                xls_form_parser = XlsFormParser('some_path', 'questionnaire_name', dbm=manager)
                fields = [{u'name': u'my_unique',
                           u'bind': {u'constraint': u'clinic'}, u'label': u'mu_uni', u'type': u'dw_idnr'}]

                get_xform_dict.return_value = fields
                is_entity_type_already_defined.return_value = True
                questions, errors, unique_id_errors = xls_form_parser._create_questions(fields)

                self.assertEqual(questions.__len__(), 1)
                self.assertDictEqual(questions[0], {'instruction': 'Answer must be a Identification Number',
                                                    'code': u'my_unique', 'title': u'mu_uni', 'required': False,
                                                    'parent_field_code': None, 'name': u'mu_uni',
                                                    'is_entity_question': True, 'type': 'unique_id',
                                                    'uniqueIdType': u'clinic'})

    def test_should_populate_error_when_constraint_not_given_for_dw_idnr_question(self):
        with patch('datawinners.blue.xform_bridge.entity_type_already_defined') as is_entity_type_already_defined:
            with patch('datawinners.blue.xform_bridge.parse_file_to_json') as get_xform_dict:
                xls_form_parser = XlsFormParser('some_path', 'questionnaire_name')
                fields = [{u'name': u'my_unique', u'label': u'mu_uni', u'type': u'dw_idnr'}]

                get_xform_dict.return_value = fields
                is_entity_type_already_defined.return_value = True
                questions, errors, unique_id_errors = xls_form_parser._create_questions(fields)

                self.assertEqual(questions.__len__(), 0)
                self.assertEqual(errors, {
                    u"The Identification Number Type (dw_idnr) is missing in the Constraints column. Please add the Identification Number Type and upload again. <a target='_blank'>Learn More</a> about how to manage Identification Numbers with XLSForms. "})

    def test_should_map_dw_idnr_question_to_select_one(self):
        # dw_idnr field in parent level, in group, in repeat inside group
        fields = {u'children': [
            {u'name': u'my_unique',
             u'bind': {u'constraint': u'clinic'}, u'label': u'mu_uni', u'type': u'dw_idnr'}, {
                u'children': [{u'bind': {u'constraint': u'clinic'}, u'type': u'dw_idnr', u'name': u'mm',
                               u'label': u'mm'}, {u'children': [
                    {u'bind': {u'constraint': u'clinic'}, u'type': u'dw_idnr', u'name': u'my_group_uni',
                     u'label': u'my_grou_uni'}, {u'type': u'text', u'name': u'text', u'label': u'ttext'}],
                                                  u'type': u'repeat', u'name': u'gr', u'label': u'gr'}],
                u'type': u'group', u'name': u'my_groupi', u'label': u'my_group'}]}

        _map_unique_id_question_to_select_one(fields)
        expected_fields = {u'children': [
            {u'bind': {}, u'choices': [{u'name': u'my_unique', u'label': u'placeholder'}], u'type': u'select one',
             u'name': u'my_unique', u'label': u'mu_uni'}, {u'label': u'my_group', u'type': u'group', u'children': [
                {u'bind': {}, u'choices': [{u'name': u'mm', u'label': u'placeholder'}], u'type': u'select one',
                 u'name': u'mm', u'label': u'mm'}, {u'label': u'gr', u'type': u'repeat', u'children': [
                    {u'bind': {}, u'choices': [{u'name': u'my_group_uni', u'label': u'placeholder'}],
                     u'type': u'select one', u'name': u'my_group_uni', u'label': u'my_grou_uni'},
                    {u'type': u'text', u'name': u'text', u'label': u'ttext'}], u'name': u'gr'}],
                                                           u'name': u'my_groupi'}]}
        self.assertDictEqual(fields, expected_fields)


class TestXformParsing(unittest.TestCase):
    def setUp(self):
        self.test_data = os.path.join(DIR, 'testdata')

    def test_should_return_generated_xform_id_for_questionnaire_with_single_explict_language(self):
        with open(os.path.join(self.test_data, 'xform-single-explict-language.xml'), "r") as file:
            xform_as_string = file.read()
            actual_generated_id = get_generated_xform_id_name(xform_as_string)
            self.assertEqual('tmpl8G0vO', actual_generated_id)
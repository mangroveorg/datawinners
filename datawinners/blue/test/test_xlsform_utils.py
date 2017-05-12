import os
import unittest
import json
from datawinners.blue.xlsform_utils import convert_excel_to_dict,\
    convert_json_to_excel, purify_posted_data
from collections import OrderedDict
import pyexcel as pe
import io
import shutil


class TestXlsFormUtils(unittest.TestCase):
    def setUp(self):
        DIR = os.path.dirname(__file__)
        self.test_data = os.path.join(DIR, 'testdata')

    def test_should_convert_json_to_excel(self):
        with open(os.path.join(self.test_data, 'household_without_fieldset_MSI_expected.json'), 'r') as input_json_file:
            input_json = json.load(input_json_file, object_pairs_hook=OrderedDict)
            expected_book_dict = pe.get_book_dict(file_name=os.path.join(self.test_data, "household_without_fieldset_MSI.xlsx"))
            actual_excel_output=convert_json_to_excel(input_json)
#             io.BufferedRandom()
#             actual_excel_output.read = lambda n=0 : actual_excel_output.getvalue()
#             actual_excel_output.readable = lambda: True
#  
#             bufferedReader = io.BufferedReader(actual_excel_output)
#             self.assertIsNotNone(bufferedReader)
            actual_book_dict = pe.get_book_dict(file_type='xlsx', file_content = actual_excel_output)
            
            self.assertEqual(actual_book_dict,expected_book_dict)
         
    def test_should_convert_excel_to_json(self):
        filename = os.path.join(self.test_data,"household_testing_excel_to_json.xlsx")
        with open(os.path.join(self.test_data, 'household_testing_excel_to_json.xlsx'), 'r') as input_file:
            file_content = input_file.read()
            excel_as_dict = convert_excel_to_dict(file_content=file_content, file_type='xlsx')
            with open(os.path.join(self.test_data, 'household_testing_excel_to_json.json'), 'r') as expected_file:
#                 json.dump(excel_as_dict, expected_file)
                excel_dump = json.dumps(excel_as_dict)
                expected_json_as_obj = json.load(expected_file)
                self.assertEqual(json.loads(excel_dump), expected_json_as_obj)

    def test_should_cover_purify_posted_data(self):
        with open(os.path.join(self.test_data, 'data_testing_empty_default_for_some_question_type.json'), 'r') as input_file:
            input_file_json = "".join(line.rstrip() for line in input_file)
            input_file_json_as_obj = json.loads(input_file_json, object_pairs_hook=OrderedDict)
            input_file_json_without_default = purify_posted_data(input_file_json_as_obj)
            with open(os.path.join(self.test_data, 'data_testing_empty_default_for_some_question_type_expected.json'), 'r') as expected_file:
                transformed_obj = json.dumps(input_file_json_without_default)
                expected_json_as_obj = json.load(expected_file)
                self.assertEqual(json.loads(transformed_obj), expected_json_as_obj)
#     def test_stringio_features(self):
#         str_io = io.StringIO()
#         str_io.write(u'First line.\n')
#         str_io.seek(0)
#         
#         with io.open(str_io, mode='wt') as buffer_reader:
#             for line in buffer_reader:
#                 print line

# Useful test for testing stream based file IO.

#     def test_should_write_excel_file_to_disk(self):
#         with open(os.path.join(self.test_data, 'household_without_fieldset_MSI_expected.json'), 'r') as input_json_file:
#             input_json = json.load(input_json_file, object_pairs_hook=OrderedDict)
#             expected_book_dict = pe.get_book_dict(file_name=os.path.join(self.test_data, "household_without_fieldset_MSI.xlsx"))
#             actual_excel_output=convert_json_to_excel(input_json)
#             with io.open(os.path.join(self.test_data, 'test_output.xlsx'), 'wb') as output_file:
#                 shutil.copyfileobj(actual_excel_output, output_file)
# #                 output_file.write(actual_excel_output.getvalue())
#                 output_file.close()
#             
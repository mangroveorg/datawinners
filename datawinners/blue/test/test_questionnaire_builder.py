# from datawinners.blue.view import ProjectBuilder
import os
import unittest
import json
from datawinners.blue.xlsform_utils import convert_excel_to_dict


DIR = os.path.dirname(__file__)
class TestQuestionnaireBuilder(unittest.TestCase):
    def setUp(self):
        self.test_data = os.path.join(DIR, 'testdata')

#     def test_should_convert_json_to_excel(self):
#         projectUpdate = ProjectUpdate()
#         builder_output = open(os.path.join(self.test_data, 'builder_output_1.json'), 'r').read()
#         projectUpdate.convert_json_to_excel(builder_output)
#         
#         pass
    def test_should_convert_excel_to_json(self):
        filename = os.path.join(self.test_data,"household_without_fieldset_MSI.xlsx")
        with open(os.path.join(self.test_data, 'household_without_fieldset_MSI.xlsx'), 'r') as input_file:
            file_content = input_file.read()
            excel_as_dict = convert_excel_to_dict(file_content=file_content, file_type='xlsx')
            with open(os.path.join(self.test_data, 'household_without_fieldset_MSI_expected.json'), 'r') as expected_file:
                expected_json_as_obj = json.load(expected_file)
                self.assertEquals(expected_json_as_obj, excel_as_dict)
        

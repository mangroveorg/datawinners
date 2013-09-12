from datawinners.entity.entity_export_helper import get_json_field_infos_for_export
from mangrove.bootstrap import initializer
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase


class TestExport(MangroveTestCase):
    def setUp(self):
        MangroveTestCase.setUp(self)
        initializer.run(self.manager)


    def test_should_get_field_instructions_for_header_in_excel_export(self):
            registration_form_model = self.manager.load_all_rows_in_view("questionnaire", key="reg")[0].get('value')
            fields, labels, codes = get_json_field_infos_for_export(registration_form_model.get('json_fields'))
            header = []
            for label in labels:
                self.assertTrue(isinstance(label, tuple))
                self.assertEqual(len(label), 3)
                header.append(label[0][0])

            self.assertEqual(['name', 'short_code', 'location', 'geo_code', 'mobile_number'], fields)
            self.assertEqual(["What is the subject's name?", "What is the subject's Unique ID Number", "What is the subject's location?","What is the subject's GPS co-ordinates?", 'What is the mobile number associated with the subject?'], header)
            self.assertEqual(['n', 's', 'l', 'g', 'm'], codes)
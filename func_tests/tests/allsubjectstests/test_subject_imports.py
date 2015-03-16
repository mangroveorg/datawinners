import os

from nose.plugins.attrib import attr
from openpyxl import load_workbook
from django.test import Client

from framework.base_test import HeadlessRunnerTest
from pages.loginpage.login_page import login
from tests.logintests.login_data import VALID_CREDENTIALS
from framework.utils.common_utils import random_number

workbook1 = {
    'subject_first_name': "FName" + random_number(2),
    'subject_last_name': "LName" + random_number(2),
    'subject_location': "Loc" + random_number(2),
    'subject_gps': '%.1f, ' % float(random_number(1)) + '%.1f' % float(random_number(1)),
    'subject_mobile_number': random_number(6)
}

workbook2 = {
    'subject_first_name': "FName" + random_number(2),
    'subject_last_name': "LName" + random_number(2),
    'subject_location': "Loc" + random_number(2),
    'subject_gps': '%.1f, ' % float(random_number(1)) + '%.1f' % float(random_number(1)),
    'subject_mobile_number': random_number(6)
}


class TestSubjectImport(HeadlessRunnerTest):
    def _assert_subject_uploaded(self, identification_number_page, workbook):
        identification_number_page.search_with(workbook['subject_first_name'])
        self.assertEqual(workbook['subject_first_name'], identification_number_page.get_cell_value(1, 2))
        self.assertEqual(workbook['subject_last_name'], identification_number_page.get_cell_value(1, 3))
        self.assertIn(workbook['subject_location'], identification_number_page.get_cell_value(1, 4))
        self.assertEqual(workbook['subject_gps'], identification_number_page.get_cell_value(1, 5))
        self.assertEqual(workbook['subject_mobile_number'], identification_number_page.get_cell_value(1, 6))

    def _prepare_workbook(self):
        file_name = 'people.xlsx'
        DIR = os.path.dirname(__file__) + '/'
        file_path = os.path.join(DIR, file_name)
        workbook = load_workbook(file_path)
        worksheet = workbook.get_sheet_by_name('people')

        worksheet['A2'] = workbook1['subject_first_name']
        worksheet['B2'] = workbook1['subject_last_name']
        worksheet['C2'] = workbook1['subject_location']
        worksheet['D2'] = workbook1['subject_gps']
        worksheet['E2'] = workbook1['subject_mobile_number']

        worksheet['A3'] = workbook2['subject_first_name']
        worksheet['B3'] = workbook2['subject_last_name']
        worksheet['C3'] = workbook2['subject_location']
        worksheet['D3'] = workbook2['subject_gps']
        worksheet['E3'] = workbook2['subject_mobile_number']
        return file_name, file_path, workbook

    @attr('functional_test')
    def test_should_import_subjects(self):
        file_name, file_path, workbook = self._prepare_workbook()
        workbook.save(file_path)
        client = Client()
        client.login(username='tester150411@gmail.com', password='tester150411')
        response = client.post(
            path='/entity/subject/import/peo/?qqfile=' + file_name,
            data=open(file_path, 'r').read(),
            content_type='application/octet-stream')
        self.assertEquals(response.status_code, 200)

        global_navigation = login(self.driver, VALID_CREDENTIALS)
        identification_number_page = global_navigation.navigate_to_all_subject_page()
        identification_number_page.select_subject_type('People')

        self._assert_subject_uploaded(identification_number_page, workbook1)
        self._assert_subject_uploaded(identification_number_page, workbook2)
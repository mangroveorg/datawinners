import os
from random import random

from django.test import Client
from nose.plugins.attrib import attr

from framework.base_test import HeadlessRunnerTest, teardown_driver
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import login
from xlutils.copy import copy
from xlrd import open_workbook
from framework.utils.common_utils import random_number

class TestAllDataSendersImport(HeadlessRunnerTest):

    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        login(cls.driver)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def _edit_datasender_import_excel(self, file_path, row):
        workbook = copy(open_workbook(file_path))
        worksheet = workbook.get_sheet(0)

        ds_name = "DsName" + random_number(2)
        ds_number = random_number(6)
        ds_location = 'loc' + random_number(2)
        ds_email = 'DsEmail' + random_number(3) + "@dw.com"
        gps_coordinates = '%.1f, ' % float(random_number(1)) + '%.1f' % float(random_number(1))

        worksheet.write(row, 0, ds_name)
        worksheet.write(row, 1, ds_number)
        worksheet.write(row, 2, ds_location)
        worksheet.write(row, 3, gps_coordinates)
        worksheet.write(row, 4, ds_email)
        workbook.save(file_path)
        return ds_email, ds_location, ds_name, ds_number, gps_coordinates

    def _upload_imported_datasender(self, file_name, file_path):
        client = Client()
        client.login(username='tester150411@gmail.com', password='tester150411')
        response = client.post(
            path='/entity/datasenders/?qqfile=' + file_name,
            data=open(file_path, 'r').read(),
            content_type='application/octet-stream')
        self.assertEquals(response.status_code, 200)

    @attr('functional_test')
    def test_should_import_more_than_one_datasender(self):
        global_navigation = GlobalNavigationPage(self.driver)
        all_datasender_page = global_navigation.navigate_to_all_data_sender_page()

        file_name = 'DataWinners_ImportDataSenders.xls'
        DIR = os.path.dirname(__file__) + '/'
        file_path = os.path.join(DIR, file_name)

        ds_email1, ds_location1, ds_name1, ds_number1, gps_coordinates1 = self._edit_datasender_import_excel(file_path, 1)

        self._upload_imported_datasender(file_name, file_path)

        all_datasender_page.search_with(ds_name1)
        self.assertEqual(ds_name1, all_datasender_page.get_cell_value(1, 2))
        self.assertIn(ds_location1, all_datasender_page.get_cell_value(1, 4))
        self.assertEqual(gps_coordinates1, all_datasender_page.get_cell_value(1, 5))
        self.assertEqual(ds_number1, all_datasender_page.get_cell_value(1, 6))
        self.assertEqual(ds_email1, all_datasender_page.get_cell_value(1, 7))

        ds_email2, ds_location2, ds_name2, ds_number2, gps_coordinates2 = self._edit_datasender_import_excel(file_path, 2)
        self._upload_imported_datasender(file_name, file_path)

        all_datasender_page.search_with(ds_name2)

        self.assertEqual(ds_name2, all_datasender_page.get_cell_value(1, 2))
        self.assertIn(ds_location2, all_datasender_page.get_cell_value(1, 4))
        self.assertEqual(gps_coordinates2, all_datasender_page.get_cell_value(1, 5))
        self.assertEqual(ds_number2, all_datasender_page.get_cell_value(1, 6))
        self.assertEqual(ds_email2, all_datasender_page.get_cell_value(1, 7))
# coding=utf-8
import json
import os
import tempfile

from django.test import Client
from nose.plugins.attrib import attr
import xlrd

from datawinners.utils import random_string
from framework.base_test import HeadlessRunnerTest
from pages.loginpage.login_page import login
from tests.advancedquestionnairetests.advanced_questionnaire_test_helper import navigate_and_verify_web_submission_page_is_loaded, perform_submission
from tests.logintests.login_data import VALID_CREDENTIALS


DIR = os.path.dirname(__file__)

@attr('functional_test')
class TestAdvancedQuestionnaireSubmissionExport(HeadlessRunnerTest):
    def setUp(self):
        self.test_data = os.path.join(DIR, 'testdata')
        self.client = Client()
        self.project_name = random_string()

    def _verify_main_sheet(self, workbook):
        self.assertEqual(
            "[u'Data Sender', u'Datasender Id', u'Submission Date', u'Status', u'Date(Year)', u'Date(Month-Year)', u'Date(DD-MM-YYYY)', u'Outer text', u'Select one outer', u'Select multiple outer', u'Date(Year)', u'Date(Month-Year)', u'Date(DD-MM-YYYY)', u'Text in a group', u'Yes or No?', u'Yes No or both', u'Date(Year)', u'Date(Month-Year)', u'Date(DD-MM-YYYY)', u'Text in a group', u'Yes or No?', u'Yes No or both', u'_index', u'_parent_index']",
            str(workbook.sheet_by_index(0).row_values(0)))
        self.assertEqual(
            "[u'Tester Pune', u'rep276']",
            str(workbook.sheet_by_index(0).row_values(1, 0, 2)))
        self.assertEqual(
            "[u'Success', 43466.0, 41791.0, 41900.0, u'Outer text', u'Yes', u'Yes; No', 43466.0, 41640.0, 41900.0, u'text in group', u'Yes', u'No', 42005.0, 41640.0, 41891.0, u'text123', u'No', u'Yes; No', 1.0, '']",
            str(workbook.sheet_by_index(0).row_values(1, 3)))
        self.assertEqual(
            "[u'Tester Pune', u'rep276']",
            str(workbook.sheet_by_index(0).row_values(2, 0, 2)))
        self.assertEqual(
            "[u'Success', 43466.0, 41791.0, 41900.0, u'Outer text', u'Yes', u'Yes; No', 43466.0, 41640.0, 41900.0, u'text in group', u'Yes', u'No', 42005.0, 41640.0, 41891.0, u'text123', u'No', u'Yes; No', 2.0, '']",
            str(workbook.sheet_by_index(0).row_values(2, 3)))
        self.assertEquals(3, workbook.sheet_by_index(0).nrows)

    def _verify_second_sheet(self, workbook):
        self.assertEqual(
            "[u'Date(Year)', u'Date(Month-Year)', u'Date(DD-MM-YYYY)', u'Text in a group', u'Yes or No?', u'Yes No or both', u'_index', u'_parent_index']",
            str(workbook.sheet_by_index(1).row_values(0, end_colx=8)))
        self.assertEqual(
            "[40544.0, 41640.0, 41907.0, u'text in group - repeat1', u'Yes', u'Yes', '', 1.0]",
            str(workbook.sheet_by_index(1).row_values(1)))
        self.assertEqual(
            "[40909.0, 41640.0, 41901.0, u'text in group - repeat2', u'No', u'Yes; No', '', 1.0]",
            str(workbook.sheet_by_index(1).row_values(2)))
        self.assertEqual(
            "[40544.0, 41640.0, 41907.0, u'text in group - repeat1', u'Yes', u'Yes', '', 2.0]",
            str(workbook.sheet_by_index(1).row_values(3)))
        self.assertEqual(
            "[40909.0, 41640.0, 41901.0, u'text in group - repeat2', u'No', u'Yes; No', '', 2.0]",
            str(workbook.sheet_by_index(1).row_values(4)))
        self.assertEquals(5, workbook.sheet_by_index(1).nrows)

    def _verify_third_sheet(self, workbook):
        self.assertEqual(
            "[u'Date(Year)', u'Date(Month-Year)', u'Date(DD-MM-YYYY)', u'Text in a group', u'Yes or No?', u'Yes No or both', u'_index', u'_parent_index']",
            str(workbook.sheet_by_index(2).row_values(0,end_colx=8)))
        self.assertEqual(
            "[40544.0, 41640.0, 41893.0, u'group22', u'No', u'Yes', '', 1.0]",
            str(workbook.sheet_by_index(2).row_values(1)))
        self.assertEqual(
            "[40544.0, 41640.0, 41894.0, u'group4', u'Yes', u'No', '', 1.0]",
            str(workbook.sheet_by_index(2).row_values(2)))
        self.assertEqual(
            "[40544.0, 41640.0, 41893.0, u'group22', u'No', u'Yes', '', 2.0]",
            str(workbook.sheet_by_index(2).row_values(3)))
        self.assertEqual(
            "[40544.0, 41640.0, 41894.0, u'group4', u'Yes', u'No', '', 2.0]",
            str(workbook.sheet_by_index(2).row_values(4)))
        self.assertEquals(5, workbook.sheet_by_index(1).nrows)

    def _verify_fourth_sheet(self, workbook):
        self.assertEqual(
            "[u'Date(Year)', u'Date(Month-Year)', u'Date(DD-MM-YYYY)', u'Text in a group', u'Yes or No?', u'Yes No or both', u'_index', u'_parent_index']",
            str(workbook.sheet_by_index(3).row_values(0, end_colx=8)))
        self.assertEqual(
            "[41640.0, 41640.0, 41896.0, u'group', u'Yes', u'Yes', '', 1.0]",
            str(workbook.sheet_by_index(3).row_values(1)))
        self.assertEqual(
            "[40179.0, 41640.0, 41892.0, u'group3', u'No', u'Yes; No', '', 1.0]",
            str(workbook.sheet_by_index(3).row_values(2)))
        self.assertEqual(
            "[41640.0, 41640.0, 41896.0, u'group', u'Yes', u'Yes', '', 2.0]",
            str(workbook.sheet_by_index(3).row_values(3)))
        self.assertEqual(
            "[40179.0, 41640.0, 41892.0, u'group3', u'No', u'Yes; No', '', 2.0]",
            str(workbook.sheet_by_index(3).row_values(4)))
        self.assertEquals(5, workbook.sheet_by_index(1).nrows)

    def test_export(self):
        self.client.login(username='tester150411@gmail.com', password='tester150411')
        self.global_navigation_page = login(self.driver, VALID_CREDENTIALS)
        questionnaire_code = self._verify_questionnaire_creation(self.project_name)
        temporary_project_name = navigate_and_verify_web_submission_page_is_loaded(self.driver,self.global_navigation_page,self.project_name)
        # Make 2 submissions
        self._do_web_submission(temporary_project_name, questionnaire_code, 'tester150411@gmail.com', 'tester150411')
        self._do_web_submission(temporary_project_name, questionnaire_code, 'tester150411@gmail.com', 'tester150411')

        resp = self.client.post('/project/export/log?type=all',
                                {'project_name': self.project_name,
                                 'search_filters': "{\"search_text\":\"\",\"dateQuestionFilters\":{}}",
                                 'questionnaire_code': questionnaire_code})

        xlfile_fd, xlfile_name = tempfile.mkstemp(".xlsx")
        os.write(xlfile_fd, resp.content)
        os.close(xlfile_fd)
        workbook = xlrd.open_workbook(xlfile_name)
        self.assertEquals(workbook.sheet_names(),
                          [u'main', u'rep_group1', u'my_repeat1_group1', u'my_outer_repeat1'])

        self._verify_main_sheet(workbook)
        self._verify_second_sheet(workbook)
        self._verify_third_sheet(workbook)
        self._verify_fourth_sheet(workbook)

    def _verify_questionnaire_creation(self, project_name):
        r = self.client.post(
            path='/xlsform/upload/?pname=' + project_name + '&qqfile=ft_advanced_questionnaire_export.xls',
            data=open(os.path.join(self.test_data, 'ft_advanced_questionnaire_export.xls'), 'r').read(),
            content_type='application/octet-stream')
        self.assertEquals(r.status_code, 200)
        self.assertNotEqual(r._container[0].find('project_name'), -1)
        response = json.loads(r._container[0])
        self.project_id = response.get('project_id')
        return response['form_code']

    def _do_web_submission(self, project_temp_name, form_code, user, password):
        credentials = {'user': user, 'password': password}
        r = perform_submission('advanced_questionnaire_export_submission.xml',project_temp_name,form_code, credentials)
        self.assertEquals(r.status_code, 201)
        self.assertNotEqual(r._container[0].find('submission_uuid'), -1)



import json
import os
import tempfile
import time
import zipfile

from nose.plugins.attrib import attr
from django.test import Client
import xlrd
from datawinners import settings

from framework.base_test import HeadlessRunnerTest, setup_driver
from framework.utils.common_utils import random_string, by_css, generate_random_email_id, by_id
from pages.advancedwebsubmissionpage.advanced_web_submission_page import AdvancedWebSubmissionPage
from pages.dataanalysispage.data_analysis_page import DataAnalysisPage
from pages.datasenderpage.data_sender_page import DataSenderPage
from pages.loginpage.login_page import login
from pages.projectdatasenderspage.project_data_senders_page import ProjectDataSendersPage
from pages.resetpasswordpage.reset_password_page import ResetPasswordPage
from pages.submissionlogpage.submission_log_locator import EDIT_BUTTON
from pages.submissionlogpage.submission_log_page import LAST_MONTH, ALL_PERIODS
from testdata.test_data import url
from tests.activateaccounttests.activate_account_data import DS_ACTIVATION_URL, NEW_PASSWORD
from tests.advancedquestionnairetests.advanced_questionnaire_test_helper import perform_submission, navigate_and_verify_web_submission_page_is_loaded, verify_advanced_web_submission_page_is_loaded
from tests.alldatasenderstests.add_data_senders_data import VALID_DATA_WITH_EMAIL
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.testsettings import UI_TEST_TIMEOUT


DIR = os.path.dirname(__file__)

regex_date_match = '\S{3}\.\W\d{2}\,\W\d{4}\,\W\d{2}:\d{2}'
SUBMISSION_DATA = 'Tester Pune rep276 ' + regex_date_match + ' Success 11.09.2014 name multiline 8 11.0 8 12.08.2016 04.2014 2016 option a,option c option b,option c option 5,option 8 option 4 No option 5 neither agree nor disagree option a option c option c   Don\'t Know Don\'t Know Don\'t Know Don\'t Know sad happy sad happy The Netherlands Amsterdam Westerpark United States New York City Harlem 9.9,8.8 10.1,9.9 recoring nuthatch -3 Grand Cape Mount County Commonwealth 2 "What is your...\n: name1", "What is your...\n: 60", "Date within a...\n: 17.09.2014";'
SUBMISSION_DATA_IMAGE = 'Tester Pune rep276 '+ regex_date_match + ' Success 1-locate.png'

class TestAdvancedQuestionnaireEndToEnd(HeadlessRunnerTest):

    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver("phantom")
        cls.test_data = os.path.join(DIR, 'testdata')
        cls.admin_email_id = 'tester150411@gmail.com'
        cls.global_navigation_page = login(cls.driver, VALID_CREDENTIALS)
        cls.client = Client()
        cls.client.login(username=cls.admin_email_id, password='tester150411')

    def _update_submission(self, project_temp_name):
        text_answer_locator = by_css('input[name="/' + project_temp_name + '/text_widgets/my_string"]')
        advanced_web_submission_page = AdvancedWebSubmissionPage(self.driver).update_text_input(text_answer_locator,
                                                                                                '-edited').submit()
        return advanced_web_submission_page

    def _edit_and_verify_submission(self, datasender_rep_id, project_temp_name):
        advanced_web_submission_page = self._update_submission(project_temp_name)
        submission_log_page = advanced_web_submission_page.navigate_to_submission_log().wait_for_table_data_to_load()
        self.assertEqual(submission_log_page.get_total_number_of_rows(), 3)  # 2 rows + 1 hidden row for select all
        submission_log_page.search(datasender_rep_id)
        data = submission_log_page.get_all_data_on_nth_row(1)
        EDITED_SUBMISSION_DATA = 'a Mickey Duck ' + datasender_rep_id + " " + regex_date_match + ' Success 11.09.2014 name-edited multiline 8 11.0 8 12.08.2016 04.2014 2016 option a,option c option b,option c option 5,option 8 option 4 No option 5 neither agree nor disagree option a option c option c   Don\'t Know Don\'t Know Don\'t Know Don\'t Know sad happy sad happy The Netherlands Amsterdam Westerpark United States New York City Harlem 9.9,8.8 10.1,9.9 recoring nuthatch -3 Grand Cape Mount County Commonwealth 2 "What is your...\n: name1", "What is your...\n: 60", "Date within a...\n: 17.09.2014";'
        self.assertRegexpMatches(" ".join(data), EDITED_SUBMISSION_DATA)

    def _verify_date_filters(self, submission_log_page):
        self.assertEqual(submission_log_page.get_date_filter_count(), 5)  # 4 date filters + 1 submission date filter
        submission_log_page.show_all_filters()
        submission_log_page.filter_by_date_question(LAST_MONTH, by_id('date-question-filter-date_time_widgets----my_date_year')) \
            .wait_for_table_data_to_load()
        self.assertEqual(submission_log_page.get_total_number_of_records(), 0)
        submission_log_page.filter_by_date_question(ALL_PERIODS, by_id('date-question-filter-date_time_widgets----my_date_year')) \
            .wait_for_table_data_to_load()
        self.assertEqual(submission_log_page.get_total_number_of_records(), 2)

    @attr('functional_test')
    def test_should_create_project_when_xlsform_is_uploaded(self):
        self.project_name = random_string()

        file_name = 'ft_advanced_questionnaire.xls'
        form_code = self._verify_questionnaire_creation(self.project_name, file_name)
        project_temp_name, web_submission_page = navigate_and_verify_web_submission_page_is_loaded(self.driver, self.global_navigation_page, self.project_name)

        web_submission_page.navigate_to_datasenders_page()
        datasender_page = ProjectDataSendersPage(self.driver)
        datasender_page.search_with("1234123413"). \
            select_a_data_sender_by_mobile_number("1234123413").perform_datasender_action(by_css(".remove"))
        datasender_page.refresh()
        datasender_page.navigate_to_analysis_page()
        DataAnalysisPage(self.driver).navigate_to_web_submission_tab()

        web_submission_page = AdvancedWebSubmissionPage(self.driver)
        self._do_web_submission('submission_data.xml', project_temp_name, form_code, self.admin_email_id, 'tester150411')
        self._verify_submission_log_page(web_submission_page)
        datasender_rep_id, ds_email = self._register_datasender()

        self.driver.wait_for_page_with_title(UI_TEST_TIMEOUT, "Data Submission")

        datasender_page = DataSenderPage(self.driver)
        datasender_page.send_in_data()
        verify_advanced_web_submission_page_is_loaded(self.driver)
        self._do_web_submission('submission_data.xml', project_temp_name, form_code, ds_email, NEW_PASSWORD)
        self.global_navigation_page.sign_out()

        self.global_navigation_page = login(self.driver, VALID_CREDENTIALS)
        submission_log_page = self.global_navigation_page.navigate_to_all_data_page().navigate_to_submission_log_page(
            self.project_name).wait_for_table_data_to_load()

        self.assertEqual(submission_log_page.get_total_number_of_records(), 2)

        self._verify_date_filters(submission_log_page)

        submission_log_page.search(datasender_rep_id)
        submission_log_page.check_submission_by_row_number(1).click_action_button().choose_on_dropdown_action(
            EDIT_BUTTON)
        verify_advanced_web_submission_page_is_loaded(self.driver)
        self._edit_and_verify_submission(datasender_rep_id, project_temp_name)

        self._verify_edit_of_questionnaire()

    def _wait_for_table_to_be_empty(self, submission_log_page):
        count = 0
        while True:
            if count > 8:
                return False
            count += 1
            if submission_log_page.get_total_number_of_records() == 0:
                return True
            time.sleep(10)
            submission_log_page.refresh()
            submission_log_page.wait_for_table_data_to_load()

        return False

    def _verify_edit_of_questionnaire(self):
        r = self.client.post(
            path='/xlsform/upload/update/' + self.project_id + "/",
            data=open(os.path.join(self.test_data, 'ft_advanced_questionnaire.xls'), 'r').read(),
            content_type='application/octet-stream')
        self.assertEquals(r.status_code, 200)
        self.assertNotEqual(r._container[0].find('"success": true'), -1, r._container[0])

        submission_log_page = self.global_navigation_page.navigate_to_all_data_page().navigate_to_submission_log_page(
            self.project_name).wait_for_table_data_to_load()

        is_table_empty = self._wait_for_table_to_be_empty(submission_log_page)
        self.driver.create_screenshot('empty_rows.png')
        self.assertTrue(is_table_empty)


    def _activate_datasender(self, email):
        r = self.client.post(path='/admin-apis/datasender/generate_token/', data={'ds_email': email})
        resp = json.loads(r._container[0])
        self.driver.go_to(url(DS_ACTIVATION_URL % (resp["user_id"], resp["token"])))
        activation_page = ResetPasswordPage(self.driver)
        activation_page.type_same_password(NEW_PASSWORD)
        activation_page.click_submit()

    def _do_web_submission(self, xml_file, project_temp_name, form_code, user, password, image_upload=False):
        r = perform_submission(xml_file, project_temp_name, form_code, {'user': user, 'password': password}, image_upload)
        self.assertEquals(r.status_code, 201)
        self.assertNotEqual(r._container[0].find('submission_uuid'), -1)

    def _verify_submission_log_page(self, web_submission_page):
        self.submission_log_page = web_submission_page.navigate_to_submission_log()
        submission = self.submission_log_page.get_all_data_on_nth_row(1)
        self.assertRegexpMatches(" ".join(submission), SUBMISSION_DATA)

    def _verify_questionnaire_creation(self, project_name, file_name):
        response = self.client.post(
            path='/xlsform/upload/?pname=' + project_name + '&qqfile='+file_name,
            data=open(os.path.join(self.test_data, file_name), 'r').read(),
            content_type='application/octet-stream')
        self.assertEquals(response.status_code, 200)
        self.assertNotEqual(response._container[0].find('project_name'), -1)
        response = json.loads(response._container[0])
        self.project_id = response.get('project_id')
        return response['form_code']

    def _register_datasender(self):
        data_sender_page = self.submission_log_page.navigate_to_datasenders_page()
        add_data_sender_page = data_sender_page.navigate_to_add_a_data_sender_page()
        email = generate_random_email_id()
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA_WITH_EMAIL, email=email)
        success_msg = add_data_sender_page.get_success_message()
        self.assertIn("Registration successful. ID is: ", success_msg)
        self._activate_datasender(email)
        return success_msg.split(": ")[1], email

    def _verify_submission_log_page_images(self, web_submission_page):
        self.submission_log_page = web_submission_page.navigate_to_submission_log()
        self.driver.wait_for_page_load()
        submission = self.submission_log_page.get_all_data_on_nth_row(1)
        cell_value = self.submission_log_page.get_data_for_row(1, 5)
        self.assertEquals(cell_value, "1-locate.png")
        self.assertRegexpMatches(" ".join(submission), SUBMISSION_DATA_IMAGE)

    def _verify_submission_log_page_image_2(self, web_submission_page):
        self.submission_log_page = web_submission_page.navigate_to_submission_log()
        web_submission_1 = self.submission_log_page.get_all_data_on_nth_row(1)
        web_submission_2 = self.submission_log_page.get_all_data_on_nth_row(2)
        self.assertListEqual([web_submission_1[0], web_submission_2[0]], ['Tester Pune rep276', 'Tester Pune rep276'])
        self.assertListEqual([web_submission_1[2], web_submission_2[2]], ['Success', 'Success'])
        self.assertIn(web_submission_1[3], ['1-locate.png', '2-locate.png'])
        self.assertIn(web_submission_2[3], ['1-locate.png', '2-locate.png'])
        self.assertRegexpMatches(web_submission_1[1], regex_date_match)
        self.assertRegexpMatches(web_submission_2[1], regex_date_match)

    def _verify_without_media(self, form_code):
        response = self.client.post('/project/export/log?type=all',
                                    {'project_name': self.project_name,
                                     'is_media': 'false',
                                     'search_filters': "{\"search_text\":\"\",\"dateQuestionFilters\":{}}",
                                     'questionnaire_code': form_code})
        xlfile_fd, xlfile_name = tempfile.mkstemp(".xls")
        os.write(xlfile_fd, response.content)
        os.close(xlfile_fd)
        workbook = xlrd.open_workbook(xlfile_name)
        self._verify_workbook_values(workbook)

    def _write_response_to_file(self, response_content):
        zip_file = tempfile.mkstemp('.zip')[1]
        file = open(zip_file, "w")
        file.write(response_content)
        file.close()
        return zip_file

    def _verify_workbook_values(self, workbook):
        self.assertEquals(workbook._sheet_list[0]._cell_values[1][0], u'Tester Pune')
        self.assertEquals(workbook._sheet_list[0]._cell_values[1][1], u'rep276')
        self.assertEquals(workbook._sheet_list[0]._cell_values[1][3], u'Success')
        self.assertEquals(workbook._sheet_list[0]._cell_values[1][4], u'1-locate.png')
        self.assertEquals(workbook._sheet_list[0]._cell_values[1][5], u'name')
        self.assertEquals(workbook._sheet_list[0]._cell_values[2][0], u'Tester Pune')
        self.assertEquals(workbook._sheet_list[0]._cell_values[2][1], u'rep276')
        self.assertEquals(workbook._sheet_list[0]._cell_values[2][3], u'Success')
        self.assertEquals(workbook._sheet_list[0]._cell_values[2][4], u'2-locate.png')
        self.assertEquals(workbook._sheet_list[0]._cell_values[1][5], u'name')


    def _verify_file_names_in_zip(self, zip_file):
        file_read = open(zip_file, 'r')
        zip_file_open = zipfile.ZipFile(file_read.name, 'r')
        expected_list = [self.project_name + '_MediaFiles_all_log/2-locate.png',
                         self.project_name + '_MediaFiles_all_log/1-locate.png',
                         self.project_name + '_all_log.xlsx']
        files_in_zip = zip_file_open.namelist()
        self.assertIn(files_in_zip[0], expected_list)
        self.assertIn(files_in_zip[1], expected_list)
        self.assertIn(files_in_zip[2], expected_list)
        return zip_file_open

    def _write_to_file_from_zip(self, zip_file_open):
        xlfile_fd, xlfile_name = tempfile.mkstemp(".xls")
        os.write(xlfile_fd, zip_file_open.read(self.project_name + '_all_log.xlsx'))
        os.close(xlfile_fd)
        return xlfile_name

    def _verify_with_media(self, form_code):
        response_content = self.client.post('/project/export/log?type=all',
                                    {'project_name': self.project_name,
                                        'is_media': 'true',
                                        'search_filters': "{\"search_text\":\"\",\"dateQuestionFilters\":{}}",
                                        'questionnaire_code': form_code}).content
        zip_file = self._write_response_to_file(response_content)
        zip_file_open = self._verify_file_names_in_zip(zip_file)
        xlfile_name = self._write_to_file_from_zip(zip_file_open)
        workbook = xlrd.open_workbook(xlfile_name)
        self._verify_workbook_values(workbook)

    @attr('functional_test')
    def test_export(self):
        self.project_name = random_string()
        client = Client()
        client.login(username=self.admin_email_id, password='tester150411')

        form_code = self._verify_questionnaire_creation(self.project_name, 'image.xlsx')
        project_temp_name, web_submission_page = navigate_and_verify_web_submission_page_is_loaded(self.driver, self.global_navigation_page, self.project_name)
        self._do_web_submission('submission_data_image.xml', project_temp_name, form_code, self.admin_email_id, 'tester150411', image_upload=True)
        self._verify_submission_log_page_images(web_submission_page)

        self._do_web_submission('submission_data_image.xml', project_temp_name, form_code, self.admin_email_id, 'tester150411',image_upload=True)
        self._verify_submission_log_page_image_2(web_submission_page)

        self._verify_without_media(form_code)
        self._verify_with_media(form_code)
import json
import os
import tempfile
import zipfile

import xlrd
from django.test import Client
from nose.plugins.attrib import attr
from nose.tools import with_setup

from framework.base_test import HeadlessRunnerTest, setup_driver, teardown_driver
from framework.utils.common_utils import random_string, by_css, generate_random_email_id, by_id
from pages.advancedwebsubmissionpage.advanced_web_submission_page import AdvancedWebSubmissionPage
from pages.dataanalysispage.data_analysis_page import DataAnalysisPage
from pages.datasenderactivationpage.activate_datasender_page import DataSenderActivationPage
from pages.datasenderpage.data_sender_page import DataSenderPage
from pages.loginpage.login_page import login, Page
from pages.projectdatasenderspage.project_data_senders_page import ProjectDataSendersPage
from pages.submissionlogpage.submission_log_locator import EDIT_BUTTON
from pages.submissionlogpage.submission_log_page import LAST_MONTH, ALL_PERIODS
from pages.warningdialog.submission_modified_dialog import SubmissionModifiedDialog
from tests.activateaccounttests.activate_account_data import NEW_PASSWORD
from tests.advancedquestionnairetests.advanced_questionnaire_test_helper import perform_submission, navigate_and_verify_web_submission_page_is_loaded, verify_advanced_web_submission_page_is_loaded,\
    navigate_and_verify_advanced_web_submission_page_is_loaded
from tests.alldatasenderstests.add_data_senders_data import VALID_DATA_WITH_EMAIL
from tests.dashboardtests.dashboard_tests_data import USER_RASITEFA_CREDENTIALS
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.testsettings import UI_TEST_TIMEOUT
from time import sleep
from pages.warningdialog.warning_dialog import WarningDialog

DIR = os.path.dirname(__file__)

regex_date_match = '\S{3}\.\W\d{2}\,\W\d{4}\,\W\d{2}:\d{2}'
SUBMISSION_DATA = 'Tester Pune rep276 ' + regex_date_match + ' Success 11.09.2014 name multiline 8 11 8 12.08.2095 04.2014 2016 option a,option c option b,option c option 5,option 8 option 4 No option 5 neither agree nor disagree option a option c option c   Don\'t Know Don\'t Know Don\'t Know Don\'t Know sad happy sad happy The Netherlands Amsterdam Westerpark United States New York City Harlem 9.9,8.8 10.1,9.9 recoring nuthatch -3 Grand Cape Mount County Commonwealth 2 "What is your...\n: name1", "What is your...\n: 60", "Date within a...\n: 17.09.2014";'
SUBMISSION_DATA_IMAGE = 'Tester Pune rep276 ' + regex_date_match + ' Success 1-locate.png'

class TestAdvancedQuestionnaireEndToEnd(HeadlessRunnerTest):
    def setUpPhantom(self):
        self.driver = setup_driver("phantom")
        self._setUp()

    def _setUp(self):
        self.test_data = os.path.join(DIR, 'testdata')
        self.admin_email_id = 'tester150411@gmail.com'
        self.global_navigation_page = login(self.driver, VALID_CREDENTIALS)
        self.client = Client()
        self.client.login(username=self.admin_email_id, password='tester150411')

    def setUpFirefox(self):
        self.driver = setup_driver("firefox")
        self._setUp()

    def tearDown(self):
        teardown_driver(self.driver)

    @classmethod
    def tearDownClass(cls):
        pass

    def _update_submission(self, project_temp_name):
        text_answer_locator = by_css('input[name="/' + project_temp_name + '/text_widgets/my_string"]')
        advanced_web_submission_page = AdvancedWebSubmissionPage(self.driver).update_text_input(text_answer_locator,
                                                                                                '-edited').submit()
        return advanced_web_submission_page

    def _edit_and_verify_submission(self, datasender_rep_id, project_temp_name, wait=False):
        advanced_web_submission_page = self._update_submission(project_temp_name)
        if wait:
            sleep(UI_TEST_TIMEOUT * 5)
        submission_log_page = advanced_web_submission_page.navigate_to_submission_log().wait_for_table_data_to_load()
        self.assertEqual(submission_log_page.get_total_number_of_rows(), 3)  # 2 rows + 1 hidden row for select all
        submission_log_page.search(datasender_rep_id)
        data = submission_log_page.get_all_data_on_nth_row(1)
        EDITED_SUBMISSION_DATA = 'a Mickey Duck ' + datasender_rep_id + " " + regex_date_match + ' Success 11.09.2014 name-edited multiline 8 11 8 12.08.2095 04.2014 2016 option a,option c option b,option c option 5,option 8 option 4 No option 5 neither agree nor disagree option a option c option c   Don\'t Know Don\'t Know Don\'t Know Don\'t Know sad happy sad happy The Netherlands Amsterdam Westerpark United States New York City Harlem 9.9,8.8 10.1,9.9 recoring nuthatch -3 Grand Cape Mount County Commonwealth 2 "What is your...\n: name1", "What is your...\n: 60", "Date within a...\n: 17.09.2014";'
        self.assertRegexpMatches(" ".join(data), EDITED_SUBMISSION_DATA)

    def _verify_date_filters(self, submission_log_page):
        self.assertEqual(submission_log_page.get_date_filter_count(), 5)  # 4 date filters + 1 submission date filter
        submission_log_page.show_all_filters()
        submission_log_page.filter_by_date_question(LAST_MONTH, by_id(
            'date-question-filter-date_time_widgets----my_date_month_year'))\
        .wait_for_table_data_to_load()
        self.assertEqual(submission_log_page.get_total_number_of_records(), 0)
        submission_log_page.filter_by_date_question(ALL_PERIODS, by_id(
            'date-question-filter-date_time_widgets----my_date_month_year'))\
        .wait_for_table_data_to_load()
        self.assertEqual(submission_log_page.get_total_number_of_records(), 2)

    def _verify_edit_of_questionnaire(self, file_name, edit_flag=False):
        edit = 'true' if edit_flag else 'false'
        r = self.client.post(
            path='/xlsform/upload/update/' + self.project_id + "/?edit=" + edit + "&qqfile=" + file_name,
            data=open(os.path.join(self.test_data, file_name), 'r').read(),
            content_type='application/octet-stream')

        self.assertEquals(r.status_code, 200)
        self.assertNotEqual(r._container[0].find('"success": true'), -1, r._container[0])

    def _activate_datasender(self, email):
        DataSenderActivationPage(self.driver).activate_datasender(email, NEW_PASSWORD)

    def _do_web_submission(self, xml_file, project_temp_name, form_code, user, password, image_upload=False):
        r = perform_submission(xml_file, project_temp_name, form_code, {'username': user, 'password': password},
                               image_upload)
        self.assertEquals(r.status_code, 201)
        self.assertNotEqual(r._container[0].find('submission_uuid'), -1)

    def _verify_submission_log_page(self, web_submission_page):
        self.submission_log_page = web_submission_page.navigate_to_submission_log()
        submission = self.submission_log_page.get_all_data_on_nth_row(1)
        self.assertRegexpMatches(" ".join(submission), SUBMISSION_DATA)

    def _verify_questionnaire_creation(self, project_name, file_name):
        response = self.client.post(
            path='/xlsform/upload/?pname=' + project_name + '&qqfile=' + file_name,
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
        if workbook._sheet_list[0]._cell_values[1][4] == u'1-locate.png':
            self.assertEquals(workbook._sheet_list[0]._cell_values[2][4], u'2-locate.png')
        else:
            self.assertEquals(workbook._sheet_list[0]._cell_values[2][4], u'1-locate.png')
            self.assertEquals(workbook._sheet_list[0]._cell_values[1][4], u'2-locate.png')

        self.assertEquals(workbook._sheet_list[0]._cell_values[1][0], u'Tester Pune')
        self.assertEquals(workbook._sheet_list[0]._cell_values[1][1], u'rep276')
        self.assertEquals(workbook._sheet_list[0]._cell_values[1][3], u'Success')
        self.assertEquals(workbook._sheet_list[0]._cell_values[1][5], u'name')
        self.assertEquals(workbook._sheet_list[0]._cell_values[1][6], u'11.02.2015 10:45:00')
        self.assertEquals(workbook._sheet_list[0]._cell_values[1][7], u'other')
        self.assertEquals(workbook._sheet_list[0]._cell_values[1][8], u'newOption')

        self.assertEquals(workbook._sheet_list[0]._cell_values[2][0], u'Tester Pune')
        self.assertEquals(workbook._sheet_list[0]._cell_values[2][1], u'rep276')
        self.assertEquals(workbook._sheet_list[0]._cell_values[2][3], u'Success')
        self.assertEquals(workbook._sheet_list[0]._cell_values[2][5], u'name')
        self.assertEquals(workbook._sheet_list[0]._cell_values[2][6], u'11.02.2015 10:45:00')
        self.assertEquals(workbook._sheet_list[0]._cell_values[2][7], u'other')
        self.assertEquals(workbook._sheet_list[0]._cell_values[2][8], u'newOption')

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
        self.assertEquals(files_in_zip.__len__(), 3)
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
    def test_should_create_project_when_xlsform_is_uploaded(self):
        self.setUpFirefox()
        self.project_name = random_string()

        file_name = 'ft_advanced_questionnaire.xls'
        form_code = self._verify_questionnaire_creation(self.project_name, file_name)
        project_temp_name, web_submission_page = navigate_and_verify_web_submission_page_is_loaded(self.driver,
                                                                                                   self.global_navigation_page
                                                                                                   , self.project_name)
        self._verify_datawinners_university()

        web_submission_page.navigate_to_datasenders_page()
        self._verify_datawinners_university()
        datasender_page = ProjectDataSendersPage(self.driver)
        datasender_page.search_with("1234123413").\
        select_a_data_sender_by_mobile_number("1234123413").perform_datasender_action(by_css(".remove"))
        datasender_page.refresh()
        datasender_page.navigate_to_analysis_page()
        self._verify_datawinners_university()
        DataAnalysisPage(self.driver).navigate_to_web_submission_tab()

        web_submission_page = AdvancedWebSubmissionPage(self.driver)
        self._do_web_submission('submission_data.xml', project_temp_name, form_code, self.admin_email_id,
                                'tester150411')
        self._verify_submission_log_page(web_submission_page)
        datasender_rep_id, ds_email = self._register_datasender()
        self._verify_datawinners_university()

        self.driver.wait_for_page_with_title(UI_TEST_TIMEOUT, "Data Submission")

        datasender_page = DataSenderPage(self.driver)
        datasender_page.send_in_data()
        verify_advanced_web_submission_page_is_loaded(self.driver)
        self._verify_datawinners_university()
        self._do_web_submission('submission_data.xml', project_temp_name, form_code, ds_email, NEW_PASSWORD)
        self.global_navigation_page.sign_out()

        self.global_navigation_page = login(self.driver, VALID_CREDENTIALS)
        submission_log_page = self.global_navigation_page.navigate_to_all_data_page().navigate_to_submission_log_page(
            self.project_name).wait_for_table_data_to_load()
        self._verify_datawinners_university()

        self.assertEqual(submission_log_page.get_total_number_of_records(), 2)

        self._verify_date_filters(submission_log_page)

        submission_log_page.search(datasender_rep_id)
        submission_log_page.check_submission_by_row_number(1).click_action_button().choose_on_dropdown_action(
            EDIT_BUTTON)
        verify_advanced_web_submission_page_is_loaded(self.driver)
        self._edit_and_verify_submission(datasender_rep_id, project_temp_name, True)

        self._verify_edit_of_questionnaire(file_name)
        self._verify_datawinners_university()

    def _verify_datawinners_university(self):
        dw_university_page = Page(self.driver)
        self.assertTrue(dw_university_page.is_help_content_available())
        dw_university_page.close_help()

    @attr('functional_test')
    def test_should_create_project_and_its_accessible_by_the_creator(self):
        self.setUpPhantom()
        self.global_navigation_page.sign_out()
        login(self.driver, USER_RASITEFA_CREDENTIALS)
        self.project_name = random_string()
        self.client.logout()
        self.client.login(username="rasitefa@mailinator.com", password="test123")
        file_name = 'ft_advanced_questionnaire.xls'
        form_code = self._verify_questionnaire_creation(self.project_name, file_name)
        self.assertEqual(len(form_code), 3)
        all_project_page = self.global_navigation_page.navigate_to_view_all_project_page()
        all_project_page.navigate_to_project_overview_page(self.project_name)
        self.assertEqual(self.driver.get_title(), u'Questionnaires - Overview')

    @attr('functional_test')
    def test_should_delete_submission_when_editflag_is_false(self):
        self.setUpPhantom()
        self.project_name = random_string()
        self.client.login(username="rasitefa@mailinator.com", password="test123")
        file_name = 'simple_advance_questionnaire.xls'
        form_code = self._verify_questionnaire_creation(self.project_name, file_name)
        self.assertEqual(len(form_code), 3)

        all_project_page = self.global_navigation_page.navigate_to_view_all_project_page()
        all_project_page.navigate_to_project_overview_page(self.project_name)
        self.assertEqual(self.driver.get_title(), u'Questionnaires - Overview')

        self._verify_edit_of_questionnaire(file_name=file_name, edit_flag=False)

        submission_log_page = self.global_navigation_page.navigate_to_all_data_page()\
        .navigate_to_submission_log_page(self.project_name).wait_for_table_data_to_load()
        self.assertTrue(submission_log_page.get_total_number_of_records() == 0)
        self.assertEquals("Text widget", submission_log_page.get_header_text(6))

    #@attr('functional_test')
    #TODO: This can't be fixed without a fix from mangrove side, skip it for the moment
    def test_should_change_label(self):
        self.project_name = random_string()
        self.client.login(username="rasitefa@mailinator.com", password="test123")
        form_code = self._verify_questionnaire_creation(self.project_name, 'simple_advance_questionnaire.xls')
        self.assertEqual(len(form_code), 3)

        all_project_page = self.global_navigation_page.navigate_to_view_all_project_page()
        all_project_page.navigate_to_project_overview_page(self.project_name)
        self.assertEqual(self.driver.get_title(), u'Questionnaires - Overview')

        project_temp_name, web_submission_page = navigate_and_verify_advanced_web_submission_page_is_loaded(self.driver,
                                                                                                            self.global_navigation_page
                                                                                                            ,
                                                                                                            self.project_name)
        self._do_web_submission('submission_test_data.xml', project_temp_name, form_code, self.admin_email_id,
                                'tester150411', image_upload=True)
        self.assertEquals(11, web_submission_page.question_count())

        self._verify_edit_of_questionnaire(file_name='simple_advance_questionnaire_label_change.xls', edit_flag=True)

        submission_log_page = self.global_navigation_page.navigate_to_all_data_page()\
        .navigate_to_submission_log_page(self.project_name).wait_for_table_data_to_load()
        self.assertFalse(submission_log_page.get_total_number_of_records() == 0)
        self.assertEquals("Updated Text widget", submission_log_page.get_header_text(6))

        project_temp_name, web_submission_page = navigate_and_verify_advanced_web_submission_page_is_loaded(self.driver,
                                                                                                            self.global_navigation_page
                                                                                                            ,
                                                                                                            self.project_name)

        self.assertEquals("No damn note to show", web_submission_page.get_note(0))

        self.assertEquals("Updated Text widget", web_submission_page.get_label(1))
        self.assertEquals("Updated Can be short or long but always one line (type = text)",
                          web_submission_page.get_hint(1))

        web_submission_page.set_input(3, 16)
        self.assertEquals("Updated Requires a number less than 10", web_submission_page.get_constraint_msg(3))

        web_submission_page.set_input(3, 12)
        self.assertFalse(web_submission_page.constraint_msg_visible(3))

        web_submission_page.set_input(3, 16)
        self.assertTrue(web_submission_page.constraint_msg_visible(3))

        self.assertFalse(web_submission_page.text_area_present(2))
        self.assertTrue(web_submission_page.input_present(2))

        self.assertEquals(11, web_submission_page.question_count())

        self.assertTrue("new_field" in web_submission_page.get_input_name(5))
        self.assertFalse(web_submission_page.input_with_name_present("my_distress"))

        self.assertTrue("20.31" in web_submission_page.get_input_value(4))

        web_submission_page.select_choice(6, 0)
        self.assertFalse(web_submission_page.is_question_visible(7))
        web_submission_page.select_choice(6, 1)
        self.assertTrue(web_submission_page.is_question_visible(7))

        self.assertFalse(web_submission_page.has_choice(8, "USD"))
        self.assertFalse(web_submission_page.has_choice(8, "Local currency"))
        self.assertTrue(web_submission_page.has_choice(8, "Dollar"))
        self.assertTrue(web_submission_page.has_choice(8, "Rupee"))

        self.assertFalse(web_submission_page.has_choice(9, "Gbarpolu"))
        self.assertTrue(web_submission_page.has_choice(9, "Golu"))

        web_submission_page.select_choice(9, 0)
        self.assertFalse(web_submission_page.has_choice(10, "Klay"))
        self.assertTrue(web_submission_page.has_choice(10, "Clay"))

    #@attr('functional_test')
    #TODO: This can't be fixed without a fix from mangrove side, skip it for the moment
    def test_should_verify_add_and_remove_question(self):
        self.setUpPhantom()
        self.project_name = random_string()
        self.client.login(username="rasitefa@mailinator.com", password="test123")
        form_code = self._verify_questionnaire_creation(self.project_name, 'simple_advance_questionnaire.xls')

        self.assertEqual(len(form_code), 3)

        all_project_page = self.global_navigation_page.navigate_to_view_all_project_page()
        all_project_page.navigate_to_project_overview_page(self.project_name)
        self.assertEqual(self.driver.get_title(), u'Questionnaires - Overview')

        project_temp_name, web_submission_page = navigate_and_verify_advanced_web_submission_page_is_loaded(self.driver,
                                                                                                            self.global_navigation_page
                                                                                                            ,
                                                                                                            self.project_name)

        self._do_web_submission('submission_test_data.xml', project_temp_name, form_code, self.admin_email_id,
                                'tester150411', image_upload=True)
        self.assertEquals(11, web_submission_page.question_count())

        self._verify_edit_of_questionnaire(file_name='simple_advance_questionnaire_add_qn.xls', edit_flag=True)
        project_temp_name, web_submission_page = navigate_and_verify_advanced_web_submission_page_is_loaded(self.driver,
                                                                                                            self.global_navigation_page
                                                                                                            ,
                                                                                                            self.project_name)
        self.assertEquals(12, web_submission_page.question_count())
        self.assertTrue(web_submission_page.has_choice(9, "Tamilnadu"))
        web_submission_page.select_choice(9, 0)
        self.assertTrue(web_submission_page.has_choice(10, "Chennai"))
        self.global_navigation_page.navigate_to_all_data_page()
        SubmissionModifiedDialog(self.driver).ignore_changes()

        self._do_web_submission('submission_test_data.xml', project_temp_name, form_code, self.admin_email_id,
                                'tester150411', image_upload=True)
        self._verify_edit_of_questionnaire(file_name='simple_advance_questionnaire.xls', edit_flag=True)
        project_temp_name, web_submission_page = navigate_and_verify_advanced_web_submission_page_is_loaded(self.driver,
                                                                                                            self.global_navigation_page
                                                                                                            ,
                                                                                                            self.project_name)
        self.assertEquals(11, web_submission_page.question_count())
        self.assertTrue(web_submission_page.has_choice(9, "Bomi"))
        web_submission_page.select_choice(9, 0)
        self.assertTrue(web_submission_page.has_choice(10, "Klay"))

    #@attr('functional_test')
    #TODO: This can't be fixed without a fix from mangrove side, skip it for the moment
    def test_should_edit_via_builder(self):
        self.setUpFirefox()
        self.project_name = random_string()
        self.client.login(username="rasitefa@mailinator.com", password="test123")
        form_code = self._verify_questionnaire_creation(self.project_name, 'simple_advance_questionnaire.xls')
        self.assertEqual(len(form_code), 3)
        projects_page = self.global_navigation_page.navigate_to_view_all_project_page()
        overview_page = projects_page.navigate_to_project_overview_page(self.project_name)
        questionnaire_tab_page = overview_page.navigate_to_questionnaire_tab()
        sleep(3)
        questionnaire_tab_page.select_question_in_builder(3)
        questionnaire_tab_page.set_question_label_in_builder(0, 'New Text Widget')
        questionnaire_tab_page.set_question_hint_in_builder(0, 'New Hint for Text Widget')

        questionnaire_tab_page.add_question_in_builder_at(11)
        questionnaire_tab_page.select_question_in_builder(11)
        questionnaire_tab_page.select_question_type_in_builder(1)
        questionnaire_tab_page.select_choice_for_question_in_builder(14, 2)
        questionnaire_tab_page.set_question_label_in_builder(1, 'New Integer Widget')
        questionnaire_tab_page.set_question_name_in_builder(1, 'new_integer')

        questionnaire_tab_page.save_questionnaire_in_builder()
        success_message = questionnaire_tab_page.get_save_success_message()
        self.assertEqual(success_message, "Successfully updated", "Saving failed")
        questionnaire_tab_page.close_save_success_message()

        project_temp_name, web_submission_page = navigate_and_verify_advanced_web_submission_page_is_loaded(self.driver,
                                                                                                            self.global_navigation_page
                                                                                                            ,
                                                                                                            self.project_name)
        self.assertEquals("New Text Widget", web_submission_page.get_label(1))
        self.assertEquals("New Hint for Text Widget", web_submission_page.get_hint(1))
        self.assertEquals("New Integer Widget", web_submission_page.get_label(11))

    @attr('functional_test')
    def test_xlsform_with_inexesistent_question_name(self):
        self.setUpPhantom()
        self.project_name = random_string()

        file_name = 'ft_advanced_questionnaire_with_inexistent_question_name.xls'
        response = self.client.post(
            path='/xlsform/upload/?pname=' + self.project_name + '&qqfile=' + file_name,
            data=open(os.path.join(self.test_data, file_name), 'r').read(),
            content_type='application/octet-stream')
        self.assertEquals(response.status_code, 200)
        response = json.loads(response._container[0])
        self.assertFalse(response.get('success'))
        expected_error_message = u"There is no question with name my_int1 for relevant in the question my_string"
        self.assertEquals(response.get('error_msg')[0], expected_error_message)

    @attr('functional_test')
    def test_export(self):
        self.setUpFirefox()
        self.project_name = random_string()
        client = Client()
        client.login(username=self.admin_email_id, password='tester150411')

        form_code = self._verify_questionnaire_creation(self.project_name, 'image.xlsx')
        project_temp_name, web_submission_page = navigate_and_verify_web_submission_page_is_loaded(self.driver,
                                                                                                   self.global_navigation_page
                                                                                                   , self.project_name)
        self._do_web_submission('submission_data_image.xml', project_temp_name, form_code, self.admin_email_id,
                                'tester150411', image_upload=True)
        self.driver.find(by_id('submission_log_link')).click()
        self.driver.find_visible_element(by_id('ignore_changes')).click()
        self._verify_submission_log_page_images(web_submission_page)

        self._do_web_submission('submission_data_image.xml', project_temp_name, form_code, self.admin_email_id,
                                'tester150411', image_upload=True)
        self._verify_submission_log_page_image_2(web_submission_page)

        self._verify_without_media(form_code)
        self._verify_with_media(form_code)


    @attr('functional_test')
    def test_edit_submisssion(self):
        self.project_name = random_string()
        self._setUp()

        form_code = self._verify_questionnaire_creation(self.project_name, 'multiple-choices.xlsx')
        project_temp_name, web_submission_page = navigate_and_verify_web_submission_page_is_loaded(self.driver,
                                                                                                   self.global_navigation_page
                                                                                                   , self.project_name)
        self._do_web_submission('edit_submission_ft-check-multiple-choices.xml', project_temp_name, form_code,
                                self.admin_email_id, 'tester150411')

        submission_log_page = self.global_navigation_page.navigate_to_all_data_page().navigate_to_submission_log_page(
            self.project_name).wait_for_table_data_to_load()
        self.driver.create_screenshot("debug-ft-sub-log-edit-nth-sub")
        web_submission_page = submission_log_page.edit_nth_submission(1)
        sleep(2)
        data = self.driver.execute_script("return dataStrToEdit;")
        self.driver.create_screenshot("debug-ft-edit-sub-page")
        expected = "<idnr>food pet rhinitis</idnr><enfant><naissance_enfant>no</naissance_enfant><poids_enfant>16</poids_enfant><nom_enfant>John</nom_enfant><date_enfant>2016-12-01</date_enfant><text>Setra</text><select_enfant>trad other</select_enfant><age_enfant>3</age_enfant></enfant><form_code>%s</form_code>" % form_code
        self.assertIn(expected, data)

        text_answer_locator = by_css('input[name="/' + project_temp_name + '/enfant/nom_enfant"]')
        web_submission_page.update_text_input(text_answer_locator, "a")

        self.assertFalse(web_submission_page.is_warning_dialog_displayed())
        web_submission_page.navigate_to_submission_log()
        sleep(1)
        self.assertTrue(web_submission_page.is_warning_dialog_displayed())
        warning_dialog = WarningDialog(self.driver,
                                       cancel_link=by_css(
                                           'div.ui-dialog[style*="block"] > div.ui-dialog-content > div > a.dialog_cancel_link'))
        warning_dialog.cancel()

        web_submission_page.submit()
        web_submission_page.wait_until_modal_dismissed()
        self.assertTrue(web_submission_page.is_success_message_tip_shown())

        web_submission_page.update_text_input(text_answer_locator, "b")
        web_submission_page.navigate_to_submission_log()
        sleep(1)
        self.assertTrue(web_submission_page.is_warning_dialog_displayed())

        warning_dialog.confirm()

        sleep(1)
        self.driver.wait_for_page_load()
        self.assertEqual(self.driver.get_title(), "Submission Log")

        

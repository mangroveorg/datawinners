import json
import os
import re

from nose.plugins.attrib import attr
from django.test import Client
import time

from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import random_string, by_css, generate_random_email_id
from pages.advancedwebsubmissionpage.advanced_web_submission_page import AdvancedWebSubmissionPage
from pages.datasenderpage.data_sender_page import DataSenderPage
from pages.loginpage.login_page import login
from pages.resetpasswordpage.reset_password_page import ResetPasswordPage
from pages.submissionlogpage.submission_log_locator import EDIT_BUTTON
from testdata.test_data import url
from tests.activateaccounttests.activate_account_data import DS_ACTIVATION_URL, NEW_PASSWORD
from tests.alldatasenderstests.add_data_senders_data import VALID_DATA_WITH_EMAIL
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.testsettings import UI_TEST_TIMEOUT


DIR = os.path.dirname(__file__)

regex_date_match = '\S{3}\.\W\d{2}\,\W\d{4}\,\W\d{2}:\d{2}\W\S{2}'
SUBMISSION_DATA = 'Tester Pune rep276 ' + regex_date_match + ' Success name multiline text 8 11.0 8 12.08.2016 04.2014 2016 option a,option c option a,option b option 8 option 5 Don\'t Know option 8 agree option d option a,option b,option c,option d option d   Don\'t Know Don\'t Know Don\'t Know Don\'t Know sad happy sad happy United States New York City Harlem The Netherlands Rotterdam Downtown 9.9,8.8 10.1,9.9 recoring nuthatch -3 Grand Cape Mount County Commonwealth 2 "What is your...\n: name1", "What is your...\n: 60";'


class TestAdvancedQuestionnaireEndToEnd(HeadlessRunnerTest):
    def setUp(self):
        self.test_data = os.path.join(DIR, 'testdata')
        self.global_navigation_page = login(self.driver, VALID_CREDENTIALS)
        self.client = Client()

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
        EDITED_SUBMISSION_DATA = 'a Mickey Duck ' + datasender_rep_id + " " + regex_date_match + ' Success name-edited multiline text 8 11.0 8 12.08.2016 04.2014 2016 option a,option c option a,option b option 8 option 5 Don\'t Know option 8 agree option d option a,option b,option c,option d option d   Don\'t Know Don\'t Know Don\'t Know Don\'t Know sad happy sad happy United States New York City Harlem The Netherlands Rotterdam Downtown 9.9,8.8 10.1,9.9 recoring nuthatch -3 Grand Cape Mount County Commonwealth 2 "What is your...\n: name1", "What is your...\n: 60";'
        self.assertRegexpMatches(" ".join(data), EDITED_SUBMISSION_DATA)

    @attr('functional_test')
    def test_should_create_project_when_xlsform_is_uploaded(self):
        self.project_name = random_string()

        self.client.login(username='tester150411@gmail.com', password='tester150411')

        form_code = self._verify_questionnaire_creation(self.project_name)
        form_element, web_submission_page = self._navigate_and_verify_web_submission_page_is_loaded()
        project_temp_name = form_element.get_attribute('id')
        self._do_web_submission(project_temp_name, form_code, 'tester150411@gmail.com', 'tester150411')
        self._verify_submission_log_page(web_submission_page)
        datasender_rep_id, ds_email = self._register_datasender()

        self.driver.wait_for_page_with_title(UI_TEST_TIMEOUT, "Data Submission")

        datasender_page = DataSenderPage(self.driver)
        datasender_page.send_in_data()
        self._verify_advanced_web_submission_page_is_loaded()
        self._do_web_submission(project_temp_name, form_code, ds_email, NEW_PASSWORD)
        self.global_navigation_page.sign_out()

        self.global_navigation_page = login(self.driver, VALID_CREDENTIALS)
        submission_log_page = self.global_navigation_page.navigate_to_all_data_page().navigate_to_submission_log_page(
            self.project_name)
        self.assertEqual(submission_log_page.get_total_number_of_records(), 2)
        submission_log_page.search(datasender_rep_id)

        submission_log_page.check_submission_by_row_number(1).click_action_button().choose_on_dropdown_action(
            EDIT_BUTTON)
        self._verify_advanced_web_submission_page_is_loaded()
        self._edit_and_verify_submission(datasender_rep_id, project_temp_name)

        self._verify_edit_of_questionnaire()

    def _wait_for_table_to_be_empty(self, submission_log_page):
        count = 0
        while True:
            if count > 5:
                return False
            count += 1
            if submission_log_page.get_total_number_of_records() == 0: #for placeholder rows
                return True
            time.sleep(10)

        return False

    def _verify_edit_of_questionnaire(self):
        r = self.client.post(
            path='/xlsform/upload/update/' + self.project_id + "/",
            data=open(os.path.join(self.test_data, 'ft_advanced_questionnaire.xls'), 'r').read(),
            content_type='application/octet-stream')
        self.assertEquals(r.status_code, 200)

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

    def _verify_advanced_web_submission_page_is_loaded(self):
        form_element = self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css("form"), True)
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".ajax-loader"))
        return form_element

    def _navigate_and_verify_web_submission_page_is_loaded(self):
        all_data_page = self.global_navigation_page.navigate_to_all_data_page()
        web_submission_page = all_data_page.navigate_to_web_submission_page(self.project_name)
        form_element = self._verify_advanced_web_submission_page_is_loaded()
        return form_element, web_submission_page

    def _do_web_submission(self, project_temp_name, form_code, user, password):
        submission_data = open(os.path.join(self.test_data, 'submission_data.xml'), 'r').read()
        submission_data = re.sub("tmpW3OW1B", project_temp_name, submission_data)
        submission_data = re.sub("<form_code>010", "<form_code>" + form_code, submission_data)
        client = Client()
        client.login(username=user, password=password)
        r = client.post(path='/xlsform/web_submission/', data={'form_data': submission_data, 'form_code': form_code})
        self.assertEquals(r.status_code, 201)
        self.assertNotEqual(r._container[0].find('submission_uuid'), -1)

    def _verify_submission_log_page(self, web_submission_page):
        self.submission_log_page = web_submission_page.navigate_to_submission_log()
        submission = self.submission_log_page.get_all_data_on_nth_row(1)
        self.assertRegexpMatches(" ".join(submission), SUBMISSION_DATA)

    def _verify_questionnaire_creation(self, project_name):
        r = self.client.post(
            path='/xlsform/upload/?pname=' + project_name + '&qqfile=ft_advanced_questionnaire.xls',
            data=open(os.path.join(self.test_data, 'ft_advanced_questionnaire.xls'), 'r').read(),
            content_type='application/octet-stream')
        self.assertEquals(r.status_code, 200)
        self.assertNotEqual(r._container[0].find('project_name'), -1)
        response = json.loads(r._container[0])
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

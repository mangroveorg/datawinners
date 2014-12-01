import json
import os

import django
from nose.plugins.attrib import attr

from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import by_css, by_id
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.loginpage.login_page import login
from pages.projectspage.projects_page import ProjectsPage
from testdata.test_data import LOGOUT
from tests.alldatasenderstests.trial_data_senders_tests import QUESTIONNAIRE_DATA
from tests.endtoendtest.end_to_end_tests import add_trial_organization_and_login
from tests.logintests.login_data import VALID_CREDENTIALS, USERNAME, PASSWORD
from tests.projects.questionnairetests.project_questionnaire_data import COPY_PROJECT_DATA
from tests.registrationtests.registration_data import REGISTRATION_PASSWORD
from tests.remindertests.reminder_data import *
from framework.utils.data_fetcher import fetch_, from_

DIR = os.path.dirname(__file__)
from django.test import Client
django.test.utils.setup_test_environment()


class TestReminderSettings(HeadlessRunnerTest):

    def setUp(self):
        self.test_data = os.path.join(DIR, 'testdata')
        self.admin_email_id = 'tester150411@gmail.com'
        self.global_navigation_page = login(self.driver, VALID_CREDENTIALS)
        self.client = Client()

    def test_verify_set_one_reminder(self):
        self.client.login(username=self.admin_email_id, password='tester150411')
        all_project_page = self.global_navigation_page.navigate_to_view_all_project_page()
        project_reminder_page = all_project_page.navigate_to_project_overview_page('Project having people as subject').navigate_to_reminder_page()
        project_id = project_reminder_page.get_project_id()
        reminder_data = {u'should_send_reminders_before_deadline': 'true',
            u'should_send_reminders_on_deadline': 'true',
            u'should_send_reminders_after_deadline': 'true',
            u'frequency_period': u'month',
            u'select_day': u'10',
            u'reminder_text_on_deadline': u'save test reminder on deadline',
            u'reminder_text_after_deadline': u'save test reminder after deadline',
            u'reminder_text_before_deadline': u'save test reminder before deadline',
            u'number_of_days_after_deadline': 6,
            u'number_of_days_before_deadline': 6,
            u'has_deadline': True,
            u'whom_to_send_message': False}

        response = self.client.post('/project/set_reminder/'+project_id+'/', data=reminder_data)
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/project/set_reminder/'+project_id+'/')
        self.assertEquals(200, response.status_code)
        reminder_saved_settings = json.loads(response.context['reminder_data'].strip("'\\"))
        reminder_data[u'should_send_reminders_before_deadline'] = True
        reminder_data[u'should_send_reminders_after_deadline'] = True
        reminder_data[u'should_send_reminders_on_deadline'] = True
        self.assertDictEqual(reminder_data, reminder_saved_settings)

class TestReminderSend(HeadlessRunnerTest):

    def tearDown(self):
        self.driver.go_to(LOGOUT)

    def go_to_reminder_page(self, project, credentials):
        global_navigation = login(self.driver, credentials)
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        overview_page = all_project_page.navigate_to_project_overview_page(project)
        return overview_page.navigate_to_reminder_page()

    def dissociate_all_datasenders_from_clinic3_project(self):
        global_navigation = login(self.driver, VALID_CREDENTIALS)
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        overview_page = all_project_page.navigate_to_project_overview_page("clinic3 test project")
        ds_page = overview_page.navigate_to_datasenders_page()
        ds_page.click_checkall_checkbox()
        number = ds_page.get_number_of_selected_datasenders()
        if number != 0 :
            ds_page.perform_datasender_action(by_css(".remove"))
            self.driver.wait_for_page_load()
        self.driver.go_to(LOGOUT)

    def set_deadline_by_month(self, reminder_settings, deadline):
        reminder_settings.set_frequency(fetch_(FREQUENCY, from_(deadline)))
        reminder_settings.set_month_day(fetch_(DAY, from_(deadline)))
        reminder_settings.set_deadline_type_for_month(fetch_(TYPE, from_(deadline)))
        return reminder_settings

    @attr("functional_test")
    def test_trial_account_should_see_reminder_not_work_message_at_reminder_tab_in_active_project(self):
        email = add_trial_organization_and_login(self.driver)
        createquestionnairepage = DashboardPage(self.driver).navigate_to_create_project_page()\
        .select_blank_questionnaire_creation_option()
        project_page = createquestionnairepage.create_questionnaire_with(COPY_PROJECT_DATA, QUESTIONNAIRE_DATA)\
        .save_and_create_project_successfully()
        project_title = project_page.get_project_title()
        self.driver.go_to(LOGOUT)
        reminder_settings = self.go_to_reminder_page(project_title, {USERNAME: email, PASSWORD: REGISTRATION_PASSWORD})
        self.assertEqual(DISABLED_REMINDER[WARNING_MESSAGE], reminder_settings.get_warning_message())
        reminder_settings.click_sent_reminder_tab()
        self.assertEqual(fetch_(WARNING_MESSAGE, from_(DISABLED_REMINDER)), reminder_settings.get_warning_message())

    @attr("functional_test")
    def test_should_display_sms_character_length_for_various_reminder_types(self):
        reminder_settings = self.go_to_reminder_page(fetch_(PROJECT_NAME, from_(DEADLINE_FIRST_DAY_OF_SAME_MONTH)), VALID_CREDENTIALS)
        self.display_sms_length_for_a_reminder_type(reminder_settings, "before")
        self.display_sms_length_for_a_reminder_type(reminder_settings, "on")
        self.display_sms_length_for_a_reminder_type(reminder_settings, "after")


    @attr('functional_test')
    def test_should_limit_sms_character_length_to_160_for_all_reminder_types(self):
        reminder_settings = self.go_to_reminder_page(fetch_(PROJECT_NAME, from_(DEADLINE_FIRST_DAY_OF_SAME_MONTH)), VALID_CREDENTIALS)
        self.limit_sms_length_for_a_reminder_type(reminder_settings, "before")
        self.limit_sms_length_for_a_reminder_type(reminder_settings, "on")
        self.limit_sms_length_for_a_reminder_type(reminder_settings, "after")

    def limit_sms_length_for_a_reminder_type(self, reminder_settings, reminder_type):
        getattr(reminder_settings, "enable_%s_deadline_reminder" % reminder_type)()
        getattr(reminder_settings, "set_message_for_%s_deadline_reminder" % reminder_type)(MESSAGE_LONGER_THAN_160)
        length = reminder_settings.get_sms_text_length_for_a_reminder_type(reminder_type)
        self.assertEqual(length, 160)

    def display_sms_length_for_a_reminder_type(self, reminder_settings, reminder_type):
        getattr(reminder_settings, "enable_%s_deadline_reminder" % reminder_type)()
        getattr(reminder_settings, "set_message_for_%s_deadline_reminder" % reminder_type)("1234567890")
        length = reminder_settings.get_sms_text_length_for_a_reminder_type(reminder_type)
        self.assertEqual(length, 10)

    @attr("functional_test")
    def test_should_disable_reminder_setting_for_project_having_no_datasender(self):
        self.dissociate_all_datasenders_from_clinic3_project()

        reminder_settings = self.go_to_reminder_page("clinic3 test project", VALID_CREDENTIALS)
        self.assertTrue(reminder_settings.is_disabled)

    # def test_should_delete_reminders_when_project_is_deleted(self):
    #     global_navigation = login(self.driver, VALID_CREDENTIALS)
    #     create_questionnaire_page = global_navigation.navigate_to_dashboard_page().navigate_to_create_project_page() \
    #         .select_blank_questionnaire_creation_option()
    #     overview_page = create_questionnaire_page.create_questionnaire_with(COPY_PROJECT_DATA,
    #                                                                         QUESTIONNAIRE_DATA).save_and_create_project_successfully()
    #     project_title = overview_page.get_project_title()
    #
    #     reminder_settings_page = overview_page.navigate_to_reminder_page()
    #     default_reminder_settings_text = reminder_settings_page.get_example_text()
    #     self._verify_reminder_setting(reminder_settings_page)
    #
    #     projects_page = global_navigation.navigate_to_view_all_project_page()
    #     projects_page.click_on_save_changes()
    #
    #     projects_page.delete_project(project_title)
    #     self._perform_undo_deletion(projects_page)
    #
    #     self._verify_default_reminder_settings(project_title,default_reminder_settings_text)

    def _verify_default_reminder_settings(self,project_name,default_reminder_message):
        self.assertEquals(default_reminder_message, ProjectsPage(self.driver).navigate_to_project_overview_page(
            project_name).navigate_to_reminder_page().get_example_text())

    def _verify_reminder_setting(self,reminder_settings_page):
        reminder_settings_page.set_deadline_by_week(fetch_(DEADLINE, from_(DEADLINE_FIRST_DAY_OF_SAME_WEEK)))

    def _perform_undo_deletion(self,projects_page):
        projects_page.trigger_undo_delete()
        self.assertTrue(self.driver.is_element_present(by_id("reminder_add_dialog_dialog_section")))
        self.driver.find_visible_element(by_css(".yes_button")).click()

    @attr("functional_test")
    def test_should_not_disable_reminder_setting_for_project_having_datasenders(self):
        reminder_settings = self.go_to_reminder_page("clinic2 test project", VALID_CREDENTIALS)
        self.assertFalse(reminder_settings.is_disabled)
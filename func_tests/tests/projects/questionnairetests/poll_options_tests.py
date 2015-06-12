from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import random_number
from pages.loginpage.login_page import login
from pages.questionnairetabpage.poll_questionnaire_page import PollQuestionnairePage
from tests.projects.questionnairetests.project_questionnaire_data import RECEIPIENT, LANGUAGES, CLINIC_ALL_DS

__author__ = 'vikas'

class TestOptionsOfPollQuestionnaire(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation = login(cls.driver)
        all_contacts_page = cls.global_navigation.navigate_to_all_data_sender_page()
        cls.unique_id = "pollcontc" + random_number(2)
        add_datasender_page = all_contacts_page.navigate_to_add_a_data_sender_page()
        add_datasender_page.create_contact(cls.unique_id)
        add_group_page = all_contacts_page.go_to_add_group_page()
        cls.group_name = "group" + random_number(3)
        add_group_page.enter_group_name(cls.group_name)
        add_group_page.click_on_add_group_button()
        all_contacts_page.add_contact_to_group(cls.unique_id, cls.group_name)
        dashboard_page = cls.global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        cls.create_questionnaire_page = create_questionnaire_options_page.select_poll_questionnaire_option()
        cls.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        cls.poll_Questionnaire_page = PollQuestionnairePage(driver=cls.driver)

    def test_should_change_language_for_automatic_reply_sms_for_poll_with_group_recipients(self):
        self.poll_Questionnaire_page.select_sms_option()
        self.poll_Questionnaire_page.enter_sms_text()
        self.poll_Questionnaire_page.select_receipient(RECEIPIENT[0], self.group_name)
        self.poll_Questionnaire_page.click_create_poll()
        self.poll_Questionnaire_page.change_automatic_reply_sms_language(LANGUAGES['fr'])
        self.assertEquals(self.poll_Questionnaire_page.is_reply_sms_language_updated(), True)

    def test_should_change_language_for_automatic_reply_sms_for_broadcast_poll(self):
        self.poll_Questionnaire_page.select_broadcast_option()
        self.poll_Questionnaire_page.click_create_poll()
        self.poll_Questionnaire_page.change_automatic_reply_sms_language(LANGUAGES['pt'])
        self.assertEquals(self.poll_Questionnaire_page.is_reply_sms_language_updated(), True)

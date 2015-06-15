from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import random_number
from pages.createquestionnairepage.create_questionnaire_locator import POLL_TAB, LINKED_CONTACTS
from pages.loginpage.login_page import login
from pages.questionnairetabpage.poll_questionnaire_page import PollQuestionnairePage
from tests.projects.questionnairetests.project_questionnaire_data import LANGUAGES, CLINIC_ALL_DS, PT, FR, \
    REP7, REP5, REP6, THIRD_COLUMN, SECOND_ROW, GROUP, THIRD_ROW, POLL_RECIPIENTS


class TestOptionsOfPollQuestionnaire(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation = login(cls.driver)

        # all_contacts_page = cls.global_navigation.navigate_to_all_data_sender_page()
        # cls.unique_id = "pollcontc" + random_number(2)
        # add_datasender_page = all_contacts_page.navigate_to_add_a_data_sender_page()
        # add_datasender_page.create_contact(cls.unique_id)
        # add_group_page = all_contacts_page.go_to_add_group_page()
        # cls.group_name = "group" + random_number(3)
        # add_group_page.enter_group_name(cls.group_name)
        # add_group_page.click_on_add_group_button()
        # all_contacts_page.add_contact_to_group(cls.unique_id, cls.group_name)

        dashboard_page = cls.global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        cls.create_questionnaire_page = create_questionnaire_options_page.select_poll_questionnaire_option()
        cls.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        cls.poll_questionnaire_page = PollQuestionnairePage(driver=cls.driver)

    def test_should_change_automatic_reply_sms_language_for_poll_with_group_recipients(self):
        self.poll_questionnaire_page.select_sms_option()
        self.poll_questionnaire_page.enter_sms_text()
        self.poll_questionnaire_page.select_receipient(LINKED_CONTACTS, CLINIC_ALL_DS)
        self.poll_questionnaire_page.click_create_poll()
        self.assertTrue(self.poll_questionnaire_page.change_automatic_reply_sms_language(LANGUAGES[FR]))
        self.assertEquals(self.poll_questionnaire_page.is_reply_sms_language_updated(), True)

    def test_should_change_automatic_reply_sms_language_for_broadcast_poll(self):
        self.poll_questionnaire_page.select_broadcast_option()
        self.poll_questionnaire_page.click_create_poll()
        self.assertTrue(self.poll_questionnaire_page.change_automatic_reply_sms_language(LANGUAGES[PT]))
        self.assertEquals(self.poll_questionnaire_page.is_reply_sms_language_updated(), True)

    def test_should_disable_automatic_reply_and_language_cannot_be_changed(self):
        self.poll_questionnaire_page.select_broadcast_option()
        self.poll_questionnaire_page.click_create_poll()
        self.driver.find(POLL_TAB).click()
        self.assertEquals(self.poll_questionnaire_page.get_automatic_reply_status(), "On")
        self.poll_questionnaire_page.change_autoamtic_reply_sms_status()
        self.assertEquals(self.poll_questionnaire_page.get_automatic_reply_status(), "Off")
        self.assertFalse(self.poll_questionnaire_page.change_automatic_reply_sms_language(LANGUAGES[PT]))
        # self.poll_questionnaire_page.deactivate_poll()

    def test_should_send_sms_to_people_selected_from_the_linked_contacts(self):
        self.poll_questionnaire_page.select_sms_option()
        self.poll_questionnaire_page.enter_sms_text()
        self.poll_questionnaire_page.select_receipient(LINKED_CONTACTS, CLINIC_ALL_DS)
        self.poll_questionnaire_page.click_create_poll()
        self.poll_questionnaire_page.select_send_sms()
        self.poll_questionnaire_page.send_sms_to(LINKED_CONTACTS, CLINIC_ALL_DS)

        self.assertTrue(self.poll_questionnaire_page.has_DS_received_sms(REP7, SECOND_ROW, THIRD_COLUMN))
        self.assertTrue(self.poll_questionnaire_page.has_DS_received_sms(REP5, SECOND_ROW, THIRD_COLUMN))
        self.assertTrue(self.poll_questionnaire_page.has_DS_received_sms(REP6, SECOND_ROW, THIRD_COLUMN))

    def test_should_send_sms_to_people_from_selected_groups(self):
        all_contacts_page = self.global_navigation.navigate_to_all_data_sender_page()
        unique_id = "pollcontc" + random_number(2)
        add_datasender_page = all_contacts_page.navigate_to_add_a_data_sender_page()
        add_datasender_page.create_contact(unique_id)
        add_group_page = all_contacts_page.go_to_add_group_page()
        group_name = "group" + random_number(3)
        add_group_page.enter_group_name(group_name)
        add_group_page.click_on_add_group_button()
        all_contacts_page.add_contact_to_group(unique_id, group_name)
        create_questionnaire_options_page = self.global_navigation.navigate_to_dashboard_page().navigate_to_create_project_page()
        self.create_questionnaire_page = create_questionnaire_options_page.select_poll_questionnaire_option()
        self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_questionnaire_page = PollQuestionnairePage(driver=self.driver)

        self.poll_questionnaire_page.select_sms_option()
        self.poll_questionnaire_page.enter_sms_text()
        self.poll_questionnaire_page.select_receipient(GROUP, group_name)
        self.poll_questionnaire_page.click_create_poll()

        self.poll_questionnaire_page.select_send_sms()
        self.poll_questionnaire_page.send_sms_to(GROUP, group_name)
        self.assertTrue(self.poll_questionnaire_page.has_DS_received_sms(unique_id, SECOND_ROW, THIRD_COLUMN))
        self.poll_questionnaire_page.click_send_sms_link()
        self.poll_questionnaire_page.send_sms_to(GROUP, group_name)
        self.assertTrue(self.poll_questionnaire_page.has_DS_received_sms(unique_id, THIRD_ROW, THIRD_COLUMN))


    def test_should_send_sms_to_own_poll_recipients(self):
        self.poll_questionnaire_page.select_sms_option()
        self.poll_questionnaire_page.enter_sms_text()
        self.poll_questionnaire_page.select_receipient(LINKED_CONTACTS, CLINIC_ALL_DS)
        self.poll_questionnaire_page.click_create_poll()
        self.poll_questionnaire_page.select_send_sms()
        # self.poll_questionnaire_page.send_sms_to(POLL_RECIPIENTS, REP7)

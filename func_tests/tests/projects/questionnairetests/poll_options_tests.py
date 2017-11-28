from time import sleep
from nose.plugins.attrib import attr
from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import random_number, by_css, by_xpath
from pages.createquestionnairepage.create_questionnaire_locator import POLL_TAB, LINKED_CONTACTS, DATA_SENDER_TAB, FIRST_CREATED_POLL_XPATH, \
    ACTIVE_POLL_NAME
from pages.globalnavigationpage.global_navigation_locator import DASHBOARD_PAGE_LINK
from pages.loginpage.login_page import login
from pages.questionnairetabpage.poll_questionnaire_page import PollQuestionnairePage
from tests.projects.questionnairetests.project_questionnaire_data import LANGUAGES, CLINIC_ALL_DS, PT, FR, \
    REP7, REP5, REP6, THIRD_COLUMN, SECOND_ROW, GROUP, THIRD_ROW, MY_POLL_RECIPIENTS, CLINIC_TEST_PROJECT, REP8, REP3, \
    REP1, SIXTH_COLUMN, FIRST_ROW, FOURTH_ROW, SIXTH_ROW, FIFTH_ROW, REP35
from tests.testsettings import UI_TEST_TIMEOUT


class TestPollOptions(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation = login(cls.driver)

    def setUp(self):
        dashboard_page = self.global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        self.create_questionnaire_page = create_questionnaire_options_page.select_poll_questionnaire_option()
        self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_questionnaire_page = PollQuestionnairePage(driver=self.driver)

    def tearDown(self):
        self.poll_questionnaire_page.delete_the_poll()

    @attr('functional_test')
    def test_should_change_automatic_reply_sms_language_for_poll_with_linked_contacts(self):
        self.poll_questionnaire_page.select_sms_option()
        self.poll_questionnaire_page.enter_sms_text()
        self.poll_questionnaire_page.select_receipient(LINKED_CONTACTS, CLINIC_ALL_DS)
        self.poll_questionnaire_page.click_create_poll()
        self.poll_questionnaire_page.change_automatic_reply_sms_language(LANGUAGES[FR])
        self.assertEquals(self.poll_questionnaire_page.is_reply_sms_language_updated(), True)

    @attr('functional_test')
    def test_should_change_automatic_reply_sms_language_for_broadcast_poll(self):
        self.poll_questionnaire_page.select_broadcast_option()
        self.poll_questionnaire_page.click_create_poll()
        self.poll_questionnaire_page.change_automatic_reply_sms_language(LANGUAGES[PT])
        self.assertEquals(self.poll_questionnaire_page.is_reply_sms_language_updated(), True)

    @attr('functional_test')
    def test_should_disable_automatic_reply_and_language_cannot_be_changed(self):
        self.poll_questionnaire_page.select_broadcast_option()
        self.poll_questionnaire_page.click_create_poll()
        self.driver.find(POLL_TAB).click()
        self.assertEquals(self.poll_questionnaire_page.get_automatic_reply_status(), "On")
        self.poll_questionnaire_page.change_autoamtic_reply_sms_status()
        sleep(2)
        self.assertEquals(self.poll_questionnaire_page.get_automatic_reply_status(), "Off")
        self.assertFalse(self.poll_questionnaire_page.change_automatic_reply_sms_language(LANGUAGES[PT]))

    @attr('functional_test')
    def test_should_send_sms_to_people_selected_from_the_linked_contacts(self):
        self.poll_questionnaire_page.select_sms_option()
        self.poll_questionnaire_page.enter_sms_text()
        self.poll_questionnaire_page.select_receipient(LINKED_CONTACTS, CLINIC_ALL_DS)
        self.poll_questionnaire_page.click_create_poll()
        self.poll_questionnaire_page.select_send_sms()
        self.poll_questionnaire_page.send_sms_to(LINKED_CONTACTS, CLINIC_TEST_PROJECT)
        recipients = [REP8, REP3, REP1, REP5, REP6, REP35]
        result = self.poll_questionnaire_page.has_DS_received_sms(recipients, FIRST_ROW, THIRD_COLUMN)
        if not result:
            self.driver.create_screenshot('failure-poll-option')
            raise Exception()
        self.assertTrue(self.poll_questionnaire_page.has_DS_received_sms(recipients, FIRST_ROW, THIRD_COLUMN))
        self.assertTrue(self.poll_questionnaire_page.has_DS_received_sms(recipients, FIRST_ROW, THIRD_COLUMN))
        self.assertTrue(self.poll_questionnaire_page.has_DS_received_sms(recipients, FIRST_ROW, THIRD_COLUMN))
        self.assertTrue(self.poll_questionnaire_page.has_DS_received_sms(recipients, FIRST_ROW, THIRD_COLUMN))
        self.assertTrue(self.poll_questionnaire_page.has_DS_received_sms(recipients, FIRST_ROW, THIRD_COLUMN))

    @attr('functional_test')
    def test_should_send_sms_to_people_from_selected_groups(self):
        group_name, unique_id = self.create_group_with_one_contact()
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

    @attr('functional_test')
    def test_should_send_sms_to_own_poll_recipients(self):
        self.poll_questionnaire_page.select_sms_option()
        self.poll_questionnaire_page.enter_sms_text()
        self.poll_questionnaire_page.select_receipient(LINKED_CONTACTS, CLINIC_ALL_DS)
        self.poll_questionnaire_page.click_create_poll()
        self.poll_questionnaire_page.select_send_sms()
        self.poll_questionnaire_page.send_sms_to(MY_POLL_RECIPIENTS, REP7)
        self.assertTrue(self.poll_questionnaire_page.has_DS_received_sms(REP7, SECOND_ROW, THIRD_COLUMN))

    @attr('functional_test')
    def test_send_sms_to_people_should_add_linked_contact_recipients_to_my_data_senders_of_poll(self):
        self.poll_questionnaire_page.select_sms_option()
        self.poll_questionnaire_page.enter_sms_text()
        self.poll_questionnaire_page.select_receipient(LINKED_CONTACTS, CLINIC_ALL_DS)
        self.poll_questionnaire_page.click_create_poll()
        self.poll_questionnaire_page.select_send_sms()
        self.poll_questionnaire_page.send_sms_to(LINKED_CONTACTS, CLINIC_TEST_PROJECT)

        self.poll_questionnaire_page.select_element(DATA_SENDER_TAB)
        self.poll_questionnaire_page.select_element(by_css('.short_code'))
        sleep(3)
        poll_recipients = self.poll_questionnaire_page.all_recipients(SIXTH_COLUMN)
        self.assertIn(REP1, poll_recipients)
        self.assertIn(REP3, poll_recipients)
        self.assertIn(REP5, poll_recipients)
        self.assertIn(REP6, poll_recipients)
        self.assertIn(REP7, poll_recipients)
        self.assertIn(REP8, poll_recipients)

    @attr('functional_test')
    def test_send_sms_to_people_should_add_group_recipients_to_my_data_senders_of_poll(self):
        group_name, unique_id = self.create_group_with_one_contact()
        self.poll_questionnaire_page.select_sms_option()
        self.poll_questionnaire_page.enter_sms_text()
        self.poll_questionnaire_page.select_receipient(LINKED_CONTACTS, CLINIC_ALL_DS)
        self.poll_questionnaire_page.click_create_poll()
        self.poll_questionnaire_page.select_send_sms()
        self.poll_questionnaire_page.send_sms_to(GROUP, group_name)
        self.poll_questionnaire_page.select_element(DATA_SENDER_TAB)
        poll_recipients = self.poll_questionnaire_page.all_recipients(SIXTH_COLUMN)
        self.assertIn(unique_id, poll_recipients)

    @attr('functional_test')
    def test_should_deactivate_the_poll(self):
        self.poll_questionnaire_page.select_broadcast_option()
        self.poll_questionnaire_page.click_create_poll()
        self.poll_questionnaire_page.deactivate_poll()
        sleep(2)
        self.assertEquals(self.poll_questionnaire_page.get_poll_status(), 'deactivated')

    @attr('functional_test')
    def test_should_activate_the_poll(self):
        self.poll_questionnaire_page.select_broadcast_option()
        self.poll_questionnaire_page.click_create_poll()
        sleep(3)
        self.poll_questionnaire_page.deactivate_poll()
        sleep(3)
        self.assertEquals(self.poll_questionnaire_page.get_poll_status(), 'deactivated')
        self.poll_questionnaire_page.activate_poll()
        sleep(3)
        self.assertEquals(self.poll_questionnaire_page.get_poll_status(), 'active')

    @attr('functional_test')
    def test_warning_message_should_come_while_activating_a_poll_when_another_poll_is_active(self):
        poll_title_1 = self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_questionnaire_page.select_broadcast_option()
        self.poll_questionnaire_page.click_create_poll()
        self.poll_questionnaire_page.deactivate_poll()
        sleep(2)
        self.global_navigation.navigate_to_dashboard_page().navigate_to_create_project_page().select_poll_questionnaire_option()
        poll_title_2 = self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_questionnaire_page.select_broadcast_option()
        self.poll_questionnaire_page.click_create_poll()
        sleep(2)
        self.global_navigation.navigate_to_all_data_page()
        previous_poll = by_xpath(FIRST_CREATED_POLL_XPATH % poll_title_1)
        self.driver.find(previous_poll).click()
        self.poll_questionnaire_page.activate_poll()
        self.assertTrue(self.poll_questionnaire_page.is_another_poll_active(poll_title_2))
        self.driver.find(ACTIVE_POLL_NAME).click()

    def create_group_with_one_contact(self):
        all_contacts_page = self.global_navigation.navigate_to_all_data_sender_page()
        unique_id = "pollcontc" + random_number(2)
        add_datasender_page = all_contacts_page.navigate_to_add_a_data_sender_page()
        add_datasender_page.create_contact(unique_id)
        add_group_page = all_contacts_page.go_to_add_group_page()
        group_name = "group" + random_number(3)
        add_group_page.enter_group_name(group_name)
        add_group_page.click_on_add_group_button()
        all_contacts_page.add_contact_to_group(unique_id, group_name)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, DASHBOARD_PAGE_LINK, True)
        create_questionnaire_options_page = self.global_navigation.navigate_to_dashboard_page().navigate_to_create_project_page()
        self.create_questionnaire_page = create_questionnaire_options_page.select_poll_questionnaire_option()
        self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        return group_name, unique_id

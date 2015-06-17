from time import sleep
from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import random_number, by_css
from pages.createquestionnairepage.create_questionnaire_locator import DATA_SENDER_TAB, POLL_TAB
from pages.loginpage.login_page import login
from pages.questionnairetabpage.poll_questionnaire_page import PollQuestionnairePage
from tests.projects.questionnairetests.project_questionnaire_data import CLINIC_ALL_DS, FIRST_ROW, SIXTH_COLUMN, \
    THIRD_COLUMN, REP6, REP5, REP7, CONTACTS_LINKED, GROUP, SECOND_ROW, THIRD_ROW


class TestCreateBlankPollQuestionnaire(HeadlessRunnerTest):

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

    @classmethod
    def tearDown(cls):
        cls.poll_questionnaire_page.delete_the_poll()


    def test_should_create_a_poll_questionnaire_with_sms_option_with_group(self):
        poll_title = self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        poll_Questionnaire_page = PollQuestionnairePage(driver=self.driver)
        poll_Questionnaire_page.select_sms_option()
        poll_Questionnaire_page.enter_sms_text()
        poll_Questionnaire_page.select_receipient(GROUP, self.group_name)
        poll_Questionnaire_page.click_create_poll()
        self.assertEquals(poll_Questionnaire_page.is_poll_created(poll_title), True)
        self.assertEquals(poll_Questionnaire_page.does_poll_has_broacast_accordians(poll_title), True)
        self.assertEquals(poll_Questionnaire_page.are_all_three_accordians_present(), True)
        self.assertEquals(poll_Questionnaire_page.is_send_sms_to_more_people_visible(), True)
        self.assertEquals(poll_Questionnaire_page.get_automatic_reply_status(), "On")

    def test_should_create_a_poll_questionnaire_with_linked_contacts(self):
        poll_title = self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        poll_Questionnaire_page = PollQuestionnairePage(driver=self.driver)
        poll_Questionnaire_page.select_sms_option()
        poll_Questionnaire_page.enter_sms_text()
        poll_Questionnaire_page.select_receipient(CONTACTS_LINKED, CLINIC_ALL_DS)
        poll_Questionnaire_page.click_create_poll()
        self.assertEquals(poll_Questionnaire_page.is_poll_created(poll_title), True)
        self.assertEquals(poll_Questionnaire_page.are_all_three_accordians_present(), True)
        self.assertEquals(poll_Questionnaire_page.is_send_sms_to_more_people_visible(), True)
        self.assertEquals(poll_Questionnaire_page.get_automatic_reply_status(), "On")

    def test_poll_should_have_data_senders_of_group_as_poll_recipient(self):
        self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        poll_Questionnaire_page = PollQuestionnairePage(driver=self.driver)
        poll_Questionnaire_page.select_sms_option()
        poll_Questionnaire_page.enter_sms_text()
        poll_Questionnaire_page.select_receipient(GROUP, self.group_name)
        poll_Questionnaire_page.click_create_poll()
        poll_Questionnaire_page.select_element(DATA_SENDER_TAB)
        self.assertEquals(poll_Questionnaire_page.isRecipientAssociated(self.unique_id, FIRST_ROW, SIXTH_COLUMN), True)

    def test_poll_should_have_data_senders_of_questionnaire_as_poll_recipients(self):
        self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        poll_Questionnaire_page = PollQuestionnairePage(driver=self.driver)
        poll_Questionnaire_page.select_sms_option()
        poll_Questionnaire_page.enter_sms_text()
        poll_Questionnaire_page.select_receipient(CONTACTS_LINKED, CLINIC_ALL_DS)
        poll_Questionnaire_page.click_create_poll()
        poll_Questionnaire_page.select_element(DATA_SENDER_TAB)
        poll_Questionnaire_page.select_element(by_css('.short_code'))
        sleep(3)
        self.assertEquals(poll_Questionnaire_page.isRecipientAssociated(REP5, FIRST_ROW, SIXTH_COLUMN), True)
        self.assertEquals(poll_Questionnaire_page.isRecipientAssociated(REP6, SECOND_ROW, SIXTH_COLUMN), True)
        self.assertEquals(poll_Questionnaire_page.isRecipientAssociated(REP7, THIRD_ROW, SIXTH_COLUMN), True)
        # self.global_navigation.navigate_to_dashboard_page().navigate_to_create_project_page().select_poll_questionnaire_option()

    def test_should_create_poll_with_broadcast_option(self):
        poll_title = self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        poll_Questionnaire_page = PollQuestionnairePage(driver=self.driver)
        poll_Questionnaire_page.select_broadcast_option()
        poll_Questionnaire_page.click_create_poll()
        self.assertEquals(poll_Questionnaire_page.does_poll_has_broacast_accordians(poll_title), True)
        self.assertEquals(poll_Questionnaire_page.are_broadcast_poll_accordians_present(), True)
        self.assertEquals(poll_Questionnaire_page.are_all_three_accordians_present(), False)
        self.assertEquals(poll_Questionnaire_page.is_send_sms_to_more_people_visible(), False)
        self.assertEquals(poll_Questionnaire_page.get_automatic_reply_status(), "On")

    def test_after_poll_creation_with_group_the_group_should_receive_sms_and_appear_in_sent_sms_table(self):
        self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        poll_Questionnaire_page = PollQuestionnairePage(driver=self.driver)
        poll_Questionnaire_page.select_sms_option()
        poll_Questionnaire_page.enter_sms_text()
        poll_Questionnaire_page.select_receipient(GROUP, self.group_name)
        poll_Questionnaire_page.click_create_poll()
        self.driver.find(POLL_TAB).click()
        self.assertEquals(poll_Questionnaire_page.has_DS_received_sms(self.unique_id, FIRST_ROW, THIRD_COLUMN), True)

    def test_after_poll_creation_with_linked_contacts_the_recipients_should_receive_sms_and_appear_in_sent_sms_table(self):
        self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        poll_Questionnaire_page = PollQuestionnairePage(driver=self.driver)
        poll_Questionnaire_page.select_sms_option()
        poll_Questionnaire_page.enter_sms_text()
        poll_Questionnaire_page.select_receipient(CONTACTS_LINKED, CLINIC_ALL_DS)
        poll_Questionnaire_page.click_create_poll()
        poll_Questionnaire_page.select_element(DATA_SENDER_TAB)
        self.assertEquals(poll_Questionnaire_page.has_DS_received_sms(REP7, FIRST_ROW, THIRD_COLUMN), True)
        self.assertEquals(poll_Questionnaire_page.has_DS_received_sms(REP5, FIRST_ROW, THIRD_COLUMN), True)
        self.assertEquals(poll_Questionnaire_page.has_DS_received_sms(REP6, FIRST_ROW, THIRD_COLUMN), True)

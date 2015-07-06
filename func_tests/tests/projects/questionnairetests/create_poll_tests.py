from time import sleep
from nose.plugins.attrib import attr
from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import random_number, by_css
from pages.createquestionnairepage.create_questionnaire_locator import DATA_SENDER_TAB, POLL_TAB, \
    poll_info_accordian, ACTIVE_POLL_NAME
from pages.globalnavigationpage.global_navigation_locator import DASHBOARD_PAGE_LINK
from pages.loginpage.login_page import login
from pages.questionnairetabpage.poll_questionnaire_page import PollQuestionnairePage
from tests.projects.questionnairetests.project_questionnaire_data import CLINIC_ALL_DS, FIRST_ROW, SIXTH_COLUMN, \
    THIRD_COLUMN, REP6, REP5, REP7, CONTACTS_LINKED, GROUP, SECOND_ROW, THIRD_ROW
from tests.testsettings import UI_TEST_TIMEOUT


class TestCreatePollQuestionnaire(HeadlessRunnerTest):

    def create_group_with_a_contact(self):
        all_contacts_page = self.global_navigation.navigate_to_all_data_sender_page()
        unique_id = "pollcontc" + random_number(2)
        add_datasender_page = all_contacts_page.navigate_to_add_a_data_sender_page()
        add_datasender_page.create_contact(unique_id)
        add_group_page = all_contacts_page.go_to_add_group_page()
        group_name = "group" + random_number(3)
        add_group_page.enter_group_name(group_name)
        add_group_page.click_on_add_group_button()
        all_contacts_page.add_contact_to_group(unique_id, group_name)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, DASHBOARD_PAGE_LINK)
        create_questionnaire_options_page = self.global_navigation.navigate_to_dashboard_page().navigate_to_create_project_page()
        self.create_Questionnaire_page = create_questionnaire_options_page.select_poll_questionnaire_option()
        return group_name, unique_id

    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation = login(cls.driver)

    def setUp(self):
        dashboard_page = self.global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        self.create_Questionnaire_page = create_questionnaire_options_page.select_poll_questionnaire_option()
        self.poll_Questionnaire_page = PollQuestionnairePage(driver=self.driver)

    def tearDown(self):
        self.poll_Questionnaire_page.delete_the_poll()

    @attr('functional_test')
    def test_should_create_a_poll_questionnaire_with_sms_option_with_group(self):
        group_name, contact_id = self.create_group_with_a_contact()
        poll_title = self.create_Questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_Questionnaire_page.select_sms_option()
        self.poll_Questionnaire_page.enter_sms_text()
        self.poll_Questionnaire_page.select_receipient(GROUP, group_name)
        self.poll_Questionnaire_page.click_create_poll()
        self.assertEquals(self.poll_Questionnaire_page.is_poll_created(poll_title), True)
        self.assertEquals(self.poll_Questionnaire_page.does_poll_has_broacast_accordians(poll_title), True)
        self.assertEquals(self.poll_Questionnaire_page.are_all_three_accordians_present(), True)
        self.assertEquals(self.poll_Questionnaire_page.is_send_sms_to_more_people_visible(), True)
        self.assertEquals(self.poll_Questionnaire_page.get_automatic_reply_status(), "On")
        self.poll_Questionnaire_page.select_element(POLL_TAB)
        self.poll_Questionnaire_page.select_element(poll_info_accordian)
        self.assertEquals(self.poll_Questionnaire_page.get_poll_status(), 'Active')


    @attr('functional_test')
    def test_should_create_a_poll_questionnaire_with_linked_contacts(self):
        poll_title = self.create_Questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_Questionnaire_page.select_sms_option()
        self.poll_Questionnaire_page.enter_sms_text()
        self.poll_Questionnaire_page.select_receipient(CONTACTS_LINKED, CLINIC_ALL_DS)
        self.poll_Questionnaire_page.click_create_poll()
        self.assertEquals(self.poll_Questionnaire_page.is_poll_created(poll_title), True)
        self.assertEquals(self.poll_Questionnaire_page.are_all_three_accordians_present(), True)
        self.assertEquals(self.poll_Questionnaire_page.is_send_sms_to_more_people_visible(), True)
        self.assertEquals(self.poll_Questionnaire_page.get_automatic_reply_status(), "On")

    @attr('functional_test')
    def test_poll_should_have_data_senders_of_group_as_poll_recipient(self):
        group_name, contact_id = self.create_group_with_a_contact()
        self.create_Questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_Questionnaire_page.select_sms_option()
        self.poll_Questionnaire_page.enter_sms_text()
        self.poll_Questionnaire_page.select_receipient(GROUP, group_name)
        self.poll_Questionnaire_page.click_create_poll()
        self.poll_Questionnaire_page.select_element(DATA_SENDER_TAB)
        self.assertEquals(self.poll_Questionnaire_page.isRecipientAssociated(contact_id, FIRST_ROW, SIXTH_COLUMN), True)


    @attr('functional_test')
    def test_poll_should_have_linked_contacts_as_poll_recipients(self):
        self.create_Questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_Questionnaire_page.select_sms_option()
        self.poll_Questionnaire_page.enter_sms_text()
        self.poll_Questionnaire_page.select_receipient(CONTACTS_LINKED, CLINIC_ALL_DS)
        self.poll_Questionnaire_page.click_create_poll()
        self.poll_Questionnaire_page.select_element(DATA_SENDER_TAB)
        self.poll_Questionnaire_page.select_element(by_css('.short_code'))
        sleep(3)
        self.assertEquals(self.poll_Questionnaire_page.isRecipientAssociated(REP5, FIRST_ROW, SIXTH_COLUMN), True)
        self.assertEquals(self.poll_Questionnaire_page.isRecipientAssociated(REP6, SECOND_ROW, SIXTH_COLUMN), True)
        self.assertEquals(self.poll_Questionnaire_page.isRecipientAssociated(REP7, THIRD_ROW, SIXTH_COLUMN), True)

    @attr('functional_test')
    def test_should_create_poll_with_broadcast_option(self):
        poll_title = self.create_Questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_Questionnaire_page.select_broadcast_option()
        self.poll_Questionnaire_page.click_create_poll()

        self.assertEquals(self.poll_Questionnaire_page.does_poll_has_broacast_accordians(poll_title), True)
        self.assertEquals(self.poll_Questionnaire_page.are_broadcast_poll_accordians_present(), True)
        self.assertEquals(self.poll_Questionnaire_page.are_all_three_accordians_present(), False)
        self.assertEquals(self.poll_Questionnaire_page.is_send_sms_to_more_people_visible(), False)
        self.assertEquals(self.poll_Questionnaire_page.get_automatic_reply_status(), "On")
        self.poll_Questionnaire_page.select_element(poll_info_accordian)
        self.assertEquals(self.poll_Questionnaire_page.get_poll_status(), 'Active')

    @attr('functional_test')
    def test_after_poll_creation_with_group_the_group_should_receive_sms_and_appear_in_sent_sms_table(self):
        group_name, contact_id = self.create_group_with_a_contact()
        self.create_Questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_Questionnaire_page.select_sms_option()
        self.poll_Questionnaire_page.enter_sms_text()
        self.poll_Questionnaire_page.select_receipient(GROUP, group_name)
        self.poll_Questionnaire_page.click_create_poll()
        self.assertEquals(self.poll_Questionnaire_page.has_DS_received_sms(contact_id, FIRST_ROW, THIRD_COLUMN), True)

    @attr('functional_test')
    def test_after_poll_creation_with_linked_contacts_the_recipients_should_receive_sms_and_appear_in_sent_sms_table(self):
        self.create_Questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_Questionnaire_page.select_sms_option()
        self.poll_Questionnaire_page.enter_sms_text()
        self.poll_Questionnaire_page.select_receipient(CONTACTS_LINKED, CLINIC_ALL_DS)
        self.poll_Questionnaire_page.click_create_poll()
        self.poll_Questionnaire_page.select_element(DATA_SENDER_TAB)

        self.assertEquals(self.poll_Questionnaire_page.has_DS_received_sms(REP7, FIRST_ROW, THIRD_COLUMN), True)
        self.assertEquals(self.poll_Questionnaire_page.has_DS_received_sms(REP5, FIRST_ROW, THIRD_COLUMN), True)
        self.assertEquals(self.poll_Questionnaire_page.has_DS_received_sms(REP6, FIRST_ROW, THIRD_COLUMN), True)

    @attr('functional_test')
    def test_a_poll_cannot_be_created_when_another_poll_is_active(self):
        poll_title = self.create_Questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_Questionnaire_page.select_broadcast_option()
        self.poll_Questionnaire_page.click_create_poll()
        self.global_navigation.navigate_to_dashboard_page().navigate_to_create_project_page()
        self.assertEquals(self.poll_Questionnaire_page.get_already_active_poll_name(), poll_title)

        self.driver.find(ACTIVE_POLL_NAME).click()
        self.poll_Questionnaire_page.deactivate_poll()

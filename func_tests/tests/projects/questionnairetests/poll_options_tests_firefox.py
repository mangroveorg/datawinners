from time import sleep
from nose.plugins.attrib import attr
from framework.base_test import HeadlessRunnerTest, setup_driver
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


class TestPollOptionsFirefox(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver("firefox")
        cls.global_navigation = login(cls.driver)

    def setUp(self):
        dashboard_page = self.global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        self.create_questionnaire_page = create_questionnaire_options_page.select_poll_questionnaire_option()
        self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_questionnaire_page = PollQuestionnairePage(driver=self.driver)

    def tearDown(self):
        self.poll_questionnaire_page.delete_the_poll()

    @attr('functional_testa')
    def test_warning_message_should_come_while_activating_a_poll_when_another_poll_is_active(self):
        poll_title_1 = self.create_questionnaire_page.set_poll_questionnaire_title("poll_questionnaire", generate_random=True)
        self.poll_questionnaire_page.select_broadcast_option()
        self.poll_questionnaire_page.click_create_poll()
        self.poll_questionnaire_page.deactivate_poll()
        sleep(1)
        dashboard = self.global_navigation.navigate_to_dashboard_page()
        sleep(1)
        project = dashboard.navigate_to_create_project_page()
        sleep(1)
        project.select_poll_questionnaire_option()
        sleep(1)
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
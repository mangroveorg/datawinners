# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from framework.base_test import setup_driver, teardown_driver, BaseTest
from nose.plugins.attrib import attr
from pages.loginpage.login_page import LoginPage
from pages.projectspage.projects_page import ProjectsPage
from testdata.test_data import *
from tests.projects.testsmsquestionnaire.project_test_sms_questionnaire_data import *
from framework.utils.common_utils import by_id
from datawinners.accountmanagement.models import MessageTracker
from datetime import datetime

@attr('suit_1')
class TestProjectTestSMSPreview(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.message_tracker = MessageTracker()
        cls.message_tracker.organization_id = 'YDC120930'
        cls.message_tracker.sms_api_usage_count = 20
        cls.message_tracker.sms_registration_count = 10
        cls.message_tracker.outgoing_sms_count = 50
        cls.message_tracker.incoming_sms_count = 50
        cls.message_tracker.incoming_sp_count = 160
        cls.message_tracker.incoming_web_count = 800
        cls.message_tracker.month = datetime.strftime(datetime.today(), "%Y-%m-01")
        cls.message_tracker.save()
        # doing successful login with valid credentials
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        cls.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

    @classmethod
    def tearDownClass(cls):
        cls.message_tracker.delete()
        teardown_driver(cls.driver)

    def setUp(self):
        pass

    def tearDown(self):
        self.global_navigation.sign_out()

    def navigate_to_clinic3_overview_page(self):
        # going on all project page
        self.driver.go_to(url("/project/"))
        all_project_page = ProjectsPage(self.driver)
        return all_project_page.navigate_to_project_overview_page(PROJECT_NAME)

    def check_upgrade_instruction(self, project_overview_page):
        light_box = project_overview_page.open_sms_tester_light_box()
        upgrade_instruction = light_box.get_upgrade_instruction_present()
        self.assertEqual(upgrade_instruction.text, UPGRADE_INSTRUCTION_MSG)

    @attr('functional_test')
    def test_should_show_upgrade_instruction_on_project_overview_page(self):
        project_overview_page = self.navigate_to_clinic3_overview_page()
        self.check_upgrade_instruction(project_overview_page)

    @attr('functional_test')
    def test_should_show_upgrade_instruction_on_my_datasenders_page(self):
        project_overview_page = self.navigate_to_clinic3_overview_page()
        project_overview_page.navigate_to_datasenders_page()
        self.driver.wait_for_page_with_title(20, MY_DATASENDERS_PAGE_TITLE)
        self.check_upgrade_instruction(project_overview_page)

    @attr('functional_test')
    def test_should_show_upgrade_instruction_on_add_datasenders_page(self):
        project_overview_page = self.navigate_to_clinic3_overview_page()
        my_datasenders = project_overview_page.navigate_to_datasenders_page()
        my_datasenders.navigate_to_add_a_data_sender_page(True)
        self.check_upgrade_instruction(project_overview_page)

    @attr('functional_test')
    def test_should_show_upgrade_instruction_on_my_subjects_page(self):
        project_overview_page = self.navigate_to_clinic3_overview_page()
        project_overview_page.navigate_to_subjects_page()
        self.driver.wait_for_page_with_title(20, MY_SUBJECTS_PAGE_TITLE)
        self.check_upgrade_instruction(project_overview_page)

    @attr('functional_test')
    def test_should_show_upgrade_instruction_on_register_subjects_page(self):
        project_overview_page = self.navigate_to_clinic3_overview_page()
        my_subjects = project_overview_page.navigate_to_subjects_page()
        my_subjects.navigate_to_subject_registration_form_tab()
        self.driver.wait_for_element(20, by_id("sms_form_heading"))
        self.check_upgrade_instruction(project_overview_page)

    @attr('functional_test')
    def test_should_show_upgrade_instruction_on_reminders_page(self):
        project_overview_page = self.navigate_to_clinic3_overview_page()
        project_overview_page.navigate_to_reminder_page()
        self.driver.wait_for_page_with_title(20, REMINDERS_PAGE_TITLE)
        self.check_upgrade_instruction(project_overview_page)

    @attr('functional_test')
    def test_should_show_upgrade_instruction_on_review_and_test_page(self):
        project_overview_page = self.navigate_to_clinic3_overview_page()
        project_overview_page.navigate_to_review_and_test()
        self.driver.wait_for_page_with_title(20, REVIEW_N_TEST_PAGE_TITLE)
        self.check_upgrade_instruction(project_overview_page)


    @attr('functional_test')
    def test_should_show_upgrade_instruction_on_data_page(self):
        project_overview_page = self.navigate_to_clinic3_overview_page()
        project_overview_page.navigate_to_data_page()
        self.driver.wait_for_page_with_title(20, DATA_ANALYSIS_PAGE_TITLE)
        self.check_upgrade_instruction(project_overview_page)

    @attr('functional_test')
    def test_should_show_upgrade_instruction_on_submission_log_page(self):
        project_overview_page = self.navigate_to_clinic3_overview_page()
        data_page = project_overview_page.navigate_to_data_page()
        data_page.navigate_to_all_data_record_page()
        self.driver.wait_for_page_with_title(20, SUBMISSION_LOG_PAGE_TITLE)
        self.check_upgrade_instruction(project_overview_page)

    @attr('functional_test')
    def test_should_show_upgrade_instruction_on_websubmission_page(self):
        project_overview_page = self.navigate_to_clinic3_overview_page()
        data_page = project_overview_page.navigate_to_data_page()
        data_page.navigate_to_web_submission_tab()
        self.driver.wait_for_page_with_title(20, WEB_SUBMISSION_PAGE_TITLE)
        self.check_upgrade_instruction(project_overview_page)

    @attr('functional_test')
    def test_should_show_upgrade_instruction_on_sendamessage_page(self):
        project_overview_page = self.navigate_to_clinic3_overview_page()
        project_overview_page.navigate_send_message_tab()
        self.driver.wait_for_page_with_title(20, SEND_MESSAGE_PAGE_TITLE)
        self.check_upgrade_instruction(project_overview_page)
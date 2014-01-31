# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest

from framework.base_test import BaseTest, setup_driver, teardown_driver
from framework.utils.common_utils import by_css
from framework.utils.data_fetcher import fetch_, from_
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.loginpage.login_page import LoginPage
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from pages.reviewpage.review_page import ReviewPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_DASHBOARD_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.reviewandtests.review_data import *
from tests.testsettings import CLOSE_BROWSER_AFTER_TEST


class TestReviewProject(BaseTest):

    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        cls.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    # def tearDown(self):
    #     import sys
    #
    #     exception_info = sys.exc_info()
    #     if exception_info != (None, None, None):
    #         import os
    #
    #         if not os.path.exists("screenshots"):
    #             os.mkdir("screenshots")
    #         self.driver.get_screenshot_as_file(
    #             "screenshots/screenshot-%s-%s.png" % (self.__class__.__name__, self._testMethodName))
    #
    #     try:
    #         if CLOSE_BROWSER_AFTER_TEST:
    #             self.driver.quit()
    #     except TypeError as e:
    #         pass

    def prerequisites_of_create_project(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        self.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(fetch_(PROJECT_NAME, from_(
            fetch_(PROJECT_PROFILE, from_(VALID_DATA)))))
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        subject_questionnaire_page = edit_project_page.save_and_create_project_successfully()
        questionnaire_page = subject_questionnaire_page.save_questionnaire_successfully()
        datsender_questionnaire_page = questionnaire_page.save_questionnaire_successfully()
        reminder_page = datsender_questionnaire_page.save_questionnnaire_successfully()
        return reminder_page.save_reminder_successfully()

    @SkipTest
    @attr('functional_test')
    def test_successful_review_of_project(self):
        review_page = self.prerequisites_of_create_project()
        self.assertEqual(fetch_(PROJECT_PROFILE, from_(VALID_DATA)), review_page.get_project_profile_details())
        review_page.open_subject_accordion()
        self.assertEqual(fetch_(SUBJECT_DETAILS, from_(VALID_DATA)), review_page.get_subject_details())
        review_page.open_questionnaire_accordion()
        self.assertEqual(fetch_(QUESTIONNAIRE, from_(VALID_DATA)), review_page.get_questionnaire())


    def login(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)


    def create_project(self,project_data=VALID_PROJECT_DATA):
        self.driver.go_to(DATA_WINNER_DASHBOARD_PAGE)
        dashboard_page = DashboardPage(self.driver)
        create_project_page = dashboard_page.navigate_to_create_project_page()
        create_project_page.create_project_with(project_data)
        create_project_page.continue_create_project()
        create_questionnaire_page = CreateQuestionnairePage(self.driver)
        self.form_code = create_questionnaire_page.get_questionnaire_code()
        create_questionnaire_page.add_question(QUESTION)
        create_questionnaire_page.save_and_create_project_successfully()

    def register_data_sender(self):
        project_overview_page = ProjectOverviewPage(self.driver)
        project_datasenders_page = project_overview_page.navigate_to_datasenders_page()
        add_data_sender_page = project_datasenders_page.navigate_to_add_a_data_sender_page()
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA_FOR_ADDING_DATASENDER)
        self.driver.wait_until_modal_dismissed()


    def prepare_data_senders(self):
        self.login()
        self.create_project()
        self.register_data_sender()
        self.driver.find(by_css("#review_tab")).click()
        return ReviewPage(self.driver)

    def test_number_of_data_senders_should_show_in_current_project(self):
        review_page = self.prepare_data_senders()
        review_page.open_data_sender_accordion()
        self.assertEqual('1', review_page.get_data_sender_count())

    def go_to_reminder_page(self, project_name):
        all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        overview_page = all_project_page.navigate_to_project_overview_page(project_name)
        return overview_page.navigate_to_reminder_page()

    def go_to_project_review_and_test_page(self, project_name):
        all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(project_name)
        return project_overview_page.navigate_to_review_and_test()

    @attr('functional_test')
    def test_should_get_reminder_status(self):
        self.create_project(project_data=REMINDER_PROJECT_DATA)
        reminders_page = self.go_to_reminder_page(fetch_(PROJECT_NAME, from_(DEADLINE_FIRST_DAY_OF_SAME_WEEK_NEW_PROJECT)))
        reminder_settings = reminders_page.click_reminder_settings_tab()
        reminder_settings = reminders_page.set_deadline_by_week(reminder_settings, fetch_(DEADLINE, from_(DEADLINE_FIRST_DAY_OF_SAME_WEEK_NEW_PROJECT)))
        reminder_settings.set_reminder(fetch_(REMINDERS, from_(DEADLINE_FIRST_DAY_OF_SAME_WEEK_NEW_PROJECT)))
        reminder_settings.set_whom_to_send(fetch_(WHOM_TO_SEND, from_(DEADLINE_FIRST_DAY_OF_SAME_WEEK_NEW_PROJECT)))
        reminder_settings.save_reminders()
        project_review = self.go_to_project_review_and_test_page(fetch_(PROJECT_NAME, from_(DEADLINE_FIRST_DAY_OF_SAME_WEEK_NEW_PROJECT)))
        self.assertEqual(project_review.get_reminder_status(), "enabled")
        reminders_page = self.go_to_reminder_page(fetch_(PROJECT_NAME, from_(DEADLINE_FIRST_DAY_OF_SAME_WEEK_NEW_PROJECT)))
        reminder_settings = reminders_page.click_reminder_settings_tab()
        reminder_settings.disable_reminder()
        reminder_settings.save_reminders()
        project_review = self.go_to_project_review_and_test_page(fetch_(PROJECT_NAME, from_(DEADLINE_FIRST_DAY_OF_SAME_WEEK_NEW_PROJECT)))
        self.assertEqual(project_review.get_reminder_status(), "disabled")
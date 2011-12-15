# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.reviewandtests.review_data import *
from tests.testsettings import CLOSE_BROWSER_AFTER_TEST
from nose.plugins.skip import SkipTest


class TestReviewProject(BaseTest):

    def tearDown(self):
        import sys

        exception_info = sys.exc_info()
        if exception_info != (None, None, None):
            import os
            if not os.path.exists("screenshots"):
                os.mkdir("screenshots")
            self.driver.get_screenshot_as_file("screenshots/screenshot-%s-%s.png" % (self.__class__.__name__, self._testMethodName))
        
        try:
            if CLOSE_BROWSER_AFTER_TEST:
                self.driver.quit()
        except TypeError as e:
            pass

    def prerequisites_of_create_project(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(fetch_(PROJECT_NAME, from_(
            fetch_(PROJECT_PROFILE, from_(VALID_DATA)))))
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        subject_questionnaire_page = edit_project_page.save_and_create_project_successfully()
        questionnaire_page = subject_questionnaire_page.save_questionnaire_successfully()
        datsender_questionnaire_page = questionnaire_page.save_questionnaire_successfully()
        reminder_page = datsender_questionnaire_page.save_questionnnaire_successfully()
        return reminder_page.save_reminder_successfully()

    @SkipTest
    @attr('functional_test', 'smoke')
    def test_successful_review_of_project(self):
        """
        Function to test the successful review of the project profile
        """
        review_page = self.prerequisites_of_create_project()
        self.assertEqual(fetch_(PROJECT_PROFILE, from_(VALID_DATA)), review_page.get_project_profile_details())
        review_page.open_subject_accordion()
        self.assertEqual(fetch_(SUBJECT_DETAILS, from_(VALID_DATA)), review_page.get_subject_details())
        review_page.open_questionnaire_accordion()
        self.assertEqual(fetch_(QUESTIONNAIRE, from_(VALID_DATA)), review_page.get_questionnaire())

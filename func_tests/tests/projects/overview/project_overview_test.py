# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from pages.loginpage.login_page import LoginPage
from pages.smsquestionnairepreviewpage.sms_questionnaire_preview_page import SmsQuestionnairePreviewPage
from testdata.test_data import *
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.projects.overview.project_overview_data import PROJECT_NAME, PREVIEW_TITLE, MC_QUESTION_CONTENT


@attr('suit_1')
class TestProjectOverview(BaseTest):
    def prerequisites_of_project_overview(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        return global_navigation.navigate_to_view_all_project_page()

    @attr('functional_test', 'smoke')
    def test_project_overview_sms_questionnaire(self):
        all_project_page = self.prerequisites_of_project_overview()
        project_overview_page = all_project_page.navigate_to_project_overview_page(PROJECT_NAME)
        light_box = project_overview_page.open_sms_questionnaire_preview()
        self.assertEqual(light_box.get_title_of_light_box(), PREVIEW_TITLE)
        sms_questionnaire_preview_page = SmsQuestionnairePreviewPage(self.driver)
        self.assertTrue(sms_questionnaire_preview_page.has_preview_steps())
        self.assertEqual(MC_QUESTION_CONTENT, sms_questionnaire_preview_page.get_question_content(5))

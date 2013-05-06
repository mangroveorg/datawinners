# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from framework.utils.global_constant import WAIT_FOR_TITLE
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.createprojecttests.create_project_data import *
from tests.createquestionnairetests.create_questionnaire_data import *

@attr('suit_1')
class TestCreateQuestionnaire(BaseTest):
    def prerequisites_of_create_questionnaire(self, project_data=VALID_DATA2):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)
        dashboard_page = DashboardPage(self.driver)
        # going on setup project page
        create_project_page = dashboard_page.navigate_to_create_project_page()
        #Navigating to Create Questionnaire Page by successfully creating a Project
        create_project_page.create_project_with(project_data)
        create_project_page.continue_create_project()
        return CreateQuestionnairePage(self.driver)

    @attr('functional_test', 'smoke')
    def test_successful_questionnaire_creation1(self):
        create_questionnaire_page = self.prerequisites_of_create_questionnaire()
        create_questionnaire_page.create_questionnaire_with(QUESTIONNAIRE_DATA)
        index = 3
        for question in fetch_(QUESTIONS, from_(QUESTIONNAIRE_DATA)):
            question_link_text = fetch_(QUESTION, from_(question))
            self.assertEquals(create_questionnaire_page.get_question_link_text(index), question_link_text)
            index += 1
        self.assertEquals(create_questionnaire_page.get_remaining_character_count(),
                          fetch_(CHARACTER_REMAINING, from_(QUESTIONNAIRE_DATA)))
        create_questionnaire_page.save_and_create_project_successfully()
        title = self.driver.wait_for_page_with_title( WAIT_FOR_TITLE, fetch_(PAGE_TITLE, from_(VALID_DATA2)))
        self.assertEquals(fetch_(PAGE_TITLE, from_(VALID_DATA2)), title)

    @attr('functional_test', 'smoke')
    def test_successful_questionnaire_creation(self):
        """
        Function to test the successful Creation of a Questionnaire with given details
        This include the test for the new code on a multiple choice question
        """
        create_questionnaire_page = self.prerequisites_of_create_questionnaire(MC_VALID_DATA)
        create_questionnaire_page.create_questionnaire_with(QUESTIONNAIRE_DATA1)
        index = 3
        for question in fetch_(QUESTIONS, from_(QUESTIONNAIRE_DATA1)):
            question_link_text = fetch_(QUESTION, from_(question))
            self.assertEquals(create_questionnaire_page.get_question_link_text(index), question_link_text)
            index += 1
        
        self.assertEqual(create_questionnaire_page.get_option_by_index_for_multiple_choice_question(60).get("text"), "2 Hyundai")

        d = create_questionnaire_page.get_option_by_index_for_multiple_choice_question(57)
        self.assertEqual(d["text"], "2 Elandra hyundai")

        create_questionnaire_page.delete_option_for_multiple_choice_question(57)
        d = create_questionnaire_page.get_option_by_index_for_multiple_choice_question(57)
        self.assertEqual(d["text"], "2 Fisker")
        
        create_questionnaire_page.save_and_create_project_successfully()
        title = self.driver.wait_for_page_with_title( WAIT_FOR_TITLE, fetch_(PAGE_TITLE, from_(VALID_DATA2)))
        self.assertEquals(fetch_(PAGE_TITLE, from_(VALID_DATA2)), title)

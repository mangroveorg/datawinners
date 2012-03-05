# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.editquestionnairetests.edit_questionnaire_data import *

@attr('suit_2')
class TestEditQuestionnaire(BaseTest):
    def prerequisites_of_edit_questionnaire(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(VALID_PROJECT_DATA)))
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        edit_project_page.continue_create_project()
        return CreateQuestionnairePage(self.driver)

    @attr('functional_test', 'smoke')
    def test_successful_questionnaire_editing(self):
        """
        Function to test the successful editing of a Questionnaire with given details
        """
        create_questionnaire_page = self.prerequisites_of_edit_questionnaire()
        questions = fetch_(QUESTIONS, from_(QUESTIONNAIRE_DATA))
        create_questionnaire_page.select_question_link(2)
        self.assertEqual(questions[0], create_questionnaire_page.get_word_type_question())
        create_questionnaire_page.select_question_link(3)
        self.assertEqual(questions[1], create_questionnaire_page.get_number_type_question())
        create_questionnaire_page.select_question_link(4)
        self.assertEqual(questions[2], create_questionnaire_page.get_date_type_question())
        create_questionnaire_page.select_question_link(5)
        self.assertEqual(questions[3], create_questionnaire_page.get_list_of_choices_type_question())
        create_questionnaire_page.select_question_link(6)
        self.assertEqual(questions[4], create_questionnaire_page.get_list_of_choices_type_question())

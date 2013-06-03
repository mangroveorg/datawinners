# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.editprojecttests.edit_project_data import *

@attr('suit_2')
class TestEditProject(BaseTest):
    def prerequisites_of_edit_project(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        return global_navigation.navigate_to_view_all_project_page()

    @attr('functional_test', 'smoke')
    def test_successful_project_editing_with_subject_change(self):
        all_project_page = self.prerequisites_of_edit_project()
        project_overview_page = all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(VALID_DATA)))
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        self.assertEqual(VALID_DATA, edit_project_page.get_project_details())
        edit_project_page.type_project_name(WATER_POINT_DATA)
        light_box = edit_project_page.edit_subject(WATER_POINT_DATA)
        self.assertEquals(light_box.get_title_of_light_box(), fetch_(TITLE, from_(LIGHT_BOX_DATA)))
        self.assertEquals(light_box.get_message_from_light_box(), fetch_(SUBJECT, from_(LIGHT_BOX_DATA)))
        edit_project_page = light_box.continue_change()
        edit_project_page.continue_create_project()
        create_questionnaire_page = CreateQuestionnairePage(self.driver)
        self.assertEqual(create_questionnaire_page.get_question_link_text(1),
                         fetch_(QUESTIONS, from_(QUESTIONNAIRE_DATA_FOR_WATER_POINT))[0])
        self.assertEqual(create_questionnaire_page.get_question_link_text(2),
                         fetch_(QUESTIONS, from_(QUESTIONNAIRE_DATA_FOR_WATER_POINT))[1])
        create_questionnaire_page.go_back()
        self.assertEqual(WATER_POINT_DATA, edit_project_page.get_project_details())

    @attr('functional_test', 'smoke')
    def test_successful_project_editing_with_report_type_change(self):
        all_project_page = self.prerequisites_of_edit_project()
        project_overview_page = all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(VALID_DATA2)))
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        self.assertEqual(VALID_DATA2, edit_project_page.get_project_details())
        edit_project_page.type_project_name(REPORTER_ACTIVITIES_DATA)
        edit_project_page.type_project_description(REPORTER_ACTIVITIES_DATA)
        light_box = edit_project_page.select_report_type(REPORTER_ACTIVITIES_DATA)
        self.assertEquals(light_box.get_title_of_light_box(), fetch_(TITLE, from_(LIGHT_BOX_DATA)))
        self.assertEquals(light_box.get_message_from_light_box(), fetch_(PROJECT, from_(LIGHT_BOX_DATA)))
        edit_project_page = light_box.continue_change()
        edit_project_page.continue_create_project()
        create_questionnaire_page = CreateQuestionnairePage(self.driver)
        self.assertEqual(create_questionnaire_page.get_question_link_text(1),
                         fetch_(QUESTIONS, from_(QUESTIONNAIRE_DATA_FOR_REPORTER_ACTIVITIES))[0])
        create_questionnaire_page.go_back()
        self.assertEqual(REPORTER_ACTIVITIES_DATA, edit_project_page.get_project_details())

# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.editprojecttests.edit_project_data import *


class TestEditProject(BaseTest):
    def prerequisites_of_edit_project(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        return global_navigation.navigate_to_view_all_project_page()

    @attr('functional_test')
    def test_should_disable_project_and_subject_change_when_editing_existing_project(self):
        all_project_page = self.prerequisites_of_edit_project()
        project_overview_page = all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(VALID_DATA)))
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        self.assertEqual(VALID_DATA, edit_project_page.get_project_details())
        light_box = edit_project_page.edit_subject(WATER_POINT_DATA)
        self.assertEquals(edit_project_page.is_individual_project_option_enabled(), False)
        self.assertEquals(edit_project_page.is_summary_project_option_enabled(), False)


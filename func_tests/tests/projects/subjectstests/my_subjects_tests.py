import unittest
from nose.plugins.attrib import attr
from framework.utils.common_utils import skipUntil
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from framework.base_test import setup_driver, teardown_driver, HeadlessRunnerTest
from pages.loginpage.login_page import LoginPage, login
from tests.projects.subjectstests.my_subjects_data import *


class TestMySubjects(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation = login(cls.driver)

    def setUp(self):
        self.all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        self.my_subjects_page = self.goto_my_subjects_page(self.all_project_page)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @classmethod
    def goto_my_subjects_page(cls, all_project_page, project_name=CLINIC_PROJECT1_NAME):
        project_overview_page = all_project_page.navigate_to_project_overview_page(project_name)
        return project_overview_page.navigate_to_subjects_page()

    @attr("functional_test")
    def test_should_load_actions_dynamically(self):
        self.my_subjects_page.navigate_to_my_subjects_list_tab()
        self.my_subjects_page.wait_for_subject_table_to_load()
        self.my_subjects_page.click_action_button()
        self.assert_none_selected_shown()

        self.my_subjects_page.select_subject_by_row(2)
        self.my_subjects_page.click_action_button()
        self.assert_action_menu_shown_for()

        self.my_subjects_page.select_subject_by_row(3)
        self.my_subjects_page.click_action_button()
        self.assertFalse(self.my_subjects_page.is_edit_disabled())

    def assert_none_selected_shown(self):
        self.assertTrue(self.my_subjects_page.is_none_selected_shown())

    def assert_action_menu_shown_for(self):
        self.assertFalse(self.my_subjects_page.is_edit_disabled())
        self.assertFalse(self.my_subjects_page.is_delete_disabled())
        self.assertFalse(self.my_subjects_page.is_none_selected_shown())

    @attr("functional_test")
    def test_should_uncheck_checkall_if_one_cb_is_unchecked(self):
        self.my_subjects_page.navigate_to_my_subjects_list_tab()
        self.my_subjects_page.wait_for_subject_table_to_load()
        self.my_subjects_page.click_checkall_checkbox()
        self.assertTrue(self.my_subjects_page.is_checkall_checked())
        self.my_subjects_page.select_subject_by_row(2)
        self.assertFalse(self.my_subjects_page.is_checkall_checked())
        self.my_subjects_page.select_subject_by_row(2)
        self.assertTrue(self.my_subjects_page.is_checkall_checked())

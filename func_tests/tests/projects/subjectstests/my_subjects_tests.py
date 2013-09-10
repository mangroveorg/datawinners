import unittest
from nose.plugins.attrib import attr
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from framework.base_test import setup_driver, teardown_driver
from pages.loginpage.login_page import LoginPage
from tests.projects.subjectstests.my_subjects_data import *


class TestMySubjects(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        cls.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

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
        self.my_subjects_page.wait_for_subject_table_to_load();
        self.my_subjects_page.click_action_button()
        self.assert_none_selected_shown()

        self.my_subjects_page.select_subject_by_row(2)
        self.my_subjects_page.click_action_button()
        self.assert_action_menu_shown_for()

        self.my_subjects_page.select_subject_by_row(3)
        self.my_subjects_page.click_action_button()
        self.assertTrue(self.my_subjects_page.is_edit_action_disabled())

    def assert_none_selected_shown(self):
        self.assertFalse(self.my_subjects_page.is_edit_action_displayed())
        self.assertFalse(self.my_subjects_page.is_delete_action_displayed())
        self.assertTrue(self.my_subjects_page.is_empty_actions_menu_shown())

    def assert_action_menu_shown_for(self):
        self.assertTrue(self.my_subjects_page.is_edit_action_displayed())
        self.assertTrue(self.my_subjects_page.is_delete_action_displayed())
        self.assertFalse(self.my_subjects_page.is_empty_actions_menu_shown())

    @attr("functional_test")
    def test_should_check_all_checkboxes(self):
        self.my_subjects_page.navigate_to_my_subjects_list_tab()
        self.my_subjects_page.wait_for_subject_table_to_load();
        self.my_subjects_page.click_checkall_checkbox()

        checked = self.my_subjects_page.get_number_of_selected_subjects()
        subjects_count = self.my_subjects_page.get_all_subjects_count()
        self.assertEqual(checked, subjects_count)

        self.my_subjects_page.click_checkall_checkbox()
        checked = self.my_subjects_page.get_number_of_selected_subjects()
        self.assertEqual(checked, 0)

    @attr("functional_test")
    def test_should_uncheck_checkall_if_one_cb_is_unchecked(self):
        self.my_subjects_page.navigate_to_my_subjects_list_tab()
        self.my_subjects_page.wait_for_subject_table_to_load();
        self.my_subjects_page.click_checkall_checkbox()
        self.assertTrue(self.my_subjects_page.is_checkall_checked())
        self.my_subjects_page.select_subject_by_row(1)
        self.assertFalse(self.my_subjects_page.is_checkall_checked())
        self.my_subjects_page.select_subject_by_row(1)
        self.assertTrue(self.my_subjects_page.is_checkall_checked())

    @attr("functional_test")
    def test_should_disable_checkall_cb_if_there_is_no_subjects(self):
        global_navigation_page = GlobalNavigationPage(self.driver)
        all_project_page = global_navigation_page.navigate_to_view_all_project_page()
        my_subjects_page = self.goto_my_subjects_page(all_project_page, "project having people as subject")
        my_subjects_page.navigate_to_my_subjects_list_tab()
        self.assertTrue(my_subjects_page.is_checkall_disabled())


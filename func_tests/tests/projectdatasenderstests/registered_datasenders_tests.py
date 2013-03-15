import unittest
from nose.plugins.attrib import attr
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from framework.base_test import setup_driver, teardown_driver
from pages.loginpage.login_page import LoginPage
from tests.projectdatasenderstests.registered_datasenders_data import *

@attr('suit_1')
class TestRegisteredDataSenders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(CLINIC_PROJECT1_NAME)
        cls.page = project_overview_page.navigate_to_datasenders_page()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @attr("functional_test")
    def test_should_load_actions_dynamically(self):
        registered_ds_page = self.page
        registered_ds_page.click_action_button()
        self.assert_none_selected_shown(registered_ds_page)

        registered_ds_page.select_a_data_sender_by_id("rep3")
        registered_ds_page.click_action_button()
        self.assert_action_menu_shown_for(registered_ds_page)

        registered_ds_page.select_a_data_sender_by_id("rep5")
        registered_ds_page.click_action_button()
        self.assertFalse(registered_ds_page.is_edit_enabled())

    def assert_none_selected_shown(self, registered_ds_page):
        self.assertTrue(registered_ds_page.is_edit_enabled())
        self.assertTrue(registered_ds_page.is_none_selected_shown())
        self.assertFalse(registered_ds_page.actions_menu_shown())

    def assert_action_menu_shown_for(self, registered_ds_page):
        self.assertFalse(registered_ds_page.is_none_selected_shown())
        self.assertTrue(registered_ds_page.actions_menu_shown())
        self.assertTrue(registered_ds_page.is_edit_enabled())
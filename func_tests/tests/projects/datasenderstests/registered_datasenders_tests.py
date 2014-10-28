import unittest
import time
from django.utils.unittest.case import SkipTest

from nose.plugins.attrib import attr

from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from framework.base_test import setup_driver, teardown_driver
from pages.loginpage.login_page import LoginPage
from tests.projects.datasenderstests.registered_datasenders_data import *
from framework.base_test import HeadlessRunnerTest


class TestRegisteredDataSenders(HeadlessRunnerTest):

    def tearDown(self):
        self.global_navigation.sign_out()

    def go_to_registered_datasenders_page(self, project_name=CLINIC_PROJECT1_NAME):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        self.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(project_name)
        return project_overview_page.navigate_to_datasenders_page()

    @attr("functional_test")
    def test_should_load_actions_dynamically(self):
        registered_ds_page = self.go_to_registered_datasenders_page()
        registered_ds_page.click_action_button()
        self.assert_none_selected_shown(registered_ds_page)

        registered_ds_page.select_a_data_sender_by_id("rep3")
        registered_ds_page.click_action_button()
        self.assert_action_menu_shown_for(registered_ds_page)

        registered_ds_page.select_a_data_sender_by_id("rep5")
        registered_ds_page.click_action_button()
        self.assertTrue(registered_ds_page.is_edit_disabled())

    def assert_none_selected_shown(self, registered_ds_page):
        self.assertTrue(registered_ds_page.is_none_selected_shown())

    def assert_action_menu_shown_for(self, registered_ds_page):
        self.assertFalse(registered_ds_page.is_none_selected_shown())
        self.assertTrue(registered_ds_page.actions_menu_shown())
        self.assertFalse(registered_ds_page.is_edit_disabled())

    @attr("functional_test")
    def test_should_check_all_checkboxes_following_master_cb(self):
        registered_ds_page = self.go_to_registered_datasenders_page()
        registered_ds_page.click_checkall_checkbox()

        checked = registered_ds_page.get_number_of_selected_datasenders()
        ds_count = registered_ds_page.get_all_datasenders_count()
        self.assertEqual(checked, ds_count)

        registered_ds_page.click_checkall_checkbox()
        self.assertEqual(registered_ds_page.get_number_of_selected_datasenders(), 0)

    @attr("functional_test")
    def test_should_uncheck_checkall_if_one_cb_is_unchecked(self):
        registered_ds_page = self.go_to_registered_datasenders_page()
        registered_ds_page.click_checkall_checkbox()
        self.assertTrue(registered_ds_page.is_checkall_checked())
        registered_ds_page.select_a_data_sender_by_id("rep3")
        self.assertFalse(registered_ds_page.is_checkall_checked())
        registered_ds_page.select_a_data_sender_by_id("rep3")
        self.assertTrue(registered_ds_page.is_checkall_checked())

    @attr("functional_test")
    def test_should_disable_checkall_cb_if_there_is_no_ds(self):
        registered_ds_page = self.go_to_registered_datasenders_page("Project having people as subject")
        if registered_ds_page.is_checkall_enabled():
            registered_ds_page.click_checkall_checkbox()
            registered_ds_page.perform_datasender_action_to_dissociate()
        for try_count in range(1,7):
            check_all_enabled = registered_ds_page.is_checkall_enabled()
            if not check_all_enabled: break;
            time.sleep(2**try_count)  # exponential back-off
        self.assertFalse(check_all_enabled, "Check all was enabled after removing all data senders from the project")


    @attr("functional_test")
    def test_should_save_changed_setting(self):
        registered_ds_page = self.go_to_registered_datasenders_page("Project having people as subject")
        registered_ds_page.open_setting_popup()
        registered_ds_page.set_setting_value('open')
        self.assertEqual(registered_ds_page.get_setting_description(), u"Everyone - Anyone with a simple phone can submit data.")
        registered_ds_page.set_setting_value("restricted")
        registered_ds_page.save_setting()
        time.sleep(3)
        self.assertEqual(registered_ds_page.get_setting_description(), u"Only Registered People - Data Senders must be registered first before submitting data.")


    @attr("functional_test")
    def test_should_revert_back_default_value_when_canceling_change(self):
        registered_ds_page = self.go_to_registered_datasenders_page("Project having people as subject")
        initial_description = registered_ds_page.get_setting_description()
        registered_ds_page.open_setting_popup()
        initial_value = registered_ds_page.get_setting_value()
        opposite_value = {'open': 'restricted', 'restricted': 'open'}
        registered_ds_page.set_setting_value(opposite_value.get(initial_value))
        self.assertNotEqual(initial_description, registered_ds_page.get_setting_description())
        registered_ds_page.click_cancel_link_on_setting_lightbox()
        self.assertEqual(initial_description, registered_ds_page.get_setting_description())
    
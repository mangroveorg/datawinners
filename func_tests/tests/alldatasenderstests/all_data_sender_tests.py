# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time

from nose.plugins.attrib import attr

from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import by_id, by_css
from framework.utils.data_fetcher import fetch_
from pages.adddatasenderspage.add_data_senders_locator import FLASH_MESSAGE_LABEL
from pages.adddatasenderspage.add_data_senders_page import AddDataSenderPage
from pages.alluserspage.all_users_page import AllUsersPage
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import login
from pages.warningdialog.delete_dialog import UserDeleteDialog, DataSenderDeleteDialog
from testdata.test_data import DATA_WINNER_ALL_DATA_SENDERS_PAGE, UNDELETE_PROJECT_URL
from tests.alldatasenderstests.all_data_sender_data import *
from pages.alldatasenderspage.all_data_senders_page import AllDataSendersPage
from tests.testsettings import UI_TEST_TIMEOUT


class TestAllDataSenders(HeadlessRunnerTest):

    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        login(cls.driver)
        cls.all_datasenders_page = AllDataSendersPage(TestAllDataSenders.driver)
        cls.datasender_id_with_web_access = cls.register_datasender(VALID_DATASENDER_WITH_WEB_ACCESS,
                                                                    id=TestAllDataSenders._create_id_for_data_sender())
        cls.datasender_id_without_web_access = cls.register_datasender(VALID_DATASENDER_WITHOUT_WEB_ACCESS,
                                                                       id=TestAllDataSenders._create_id_for_data_sender())
        cls.user_mobile_number = TestAllDataSenders.add_new_user(NEW_USER_DATA)
        cls.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        cls.all_datasenders_page.wait_for_table_to_load()
        cls.all_datasenders_page.search_with(cls.user_mobile_number)
        cls.user_ID = cls.all_datasenders_page.get_cell_value(1, 3)

    def setUp(self):
        self.all_datasenders_page.load()

    @classmethod
    def _create_id_for_data_sender(cls):
        return "allds" + random_number(4)


    @classmethod
    def register_datasender(cls, datasender_details, id=None):
        cls.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        add_data_sender_page = cls.all_datasenders_page.navigate_to_add_a_data_sender_page()
        add_data_sender_page.enter_data_sender_details_from(datasender_details, unique_id=id)
        return add_data_sender_page.get_rep_id_from_success_message(add_data_sender_page.get_success_message()) if id is None else id

    @attr('functional_tests')
    def test_links(self):
        self.all_datasenders_page.check_links()

    @attr('functional_test')
    def test_successful_association_and_dissociation_of_data_sender(self):
        self.all_datasenders_page.search_with(self.datasender_id_without_web_access)
        self.assertEqual("", self.all_datasenders_page.get_project_names(self.datasender_id_without_web_access))
        self.all_datasenders_page.associate_datasender_to_projects(self.datasender_id_without_web_access,
                                                                   ["clinic test project1", "clinic2 test project"])
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_id("datasender_table_processing"))

        self.assertEqual("clinic test project1, clinic2 test project",
                         self.all_datasenders_page.get_project_names(self.datasender_id_without_web_access))
        self.all_datasenders_page.dissociate_datasender_from_project(self.datasender_id_without_web_access,
                                                                     "clinic test project1")
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_id("datasender_table_processing"))
        self.assertEqual("clinic2 test project",
                         self.all_datasenders_page.get_project_names(self.datasender_id_without_web_access))
        self.all_datasenders_page.dissociate_datasender_from_project(self.datasender_id_without_web_access,
                                                                     "clinic2 test project")
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_id("datasender_table_processing"))
        self.assertEqual("", self.all_datasenders_page.get_project_names(self.datasender_id_without_web_access))

    @attr('functional_test')
    def test_dissociate_ds_without_selecting_project(self):
        self.all_datasenders_page.search_with(self.datasender_id_without_web_access)
        self.all_datasenders_page.select_a_data_sender_by_id(self.datasender_id_without_web_access)
        self.all_datasenders_page.perform_datasender_action(DISSOCIATE)
        self.all_datasenders_page.click_confirm()
        self.assertEqual(self.all_datasenders_page.get_error_message(), ERROR_MSG_FOR_NOT_SELECTING_PROJECT)

    @attr('functional_test')
    def test_associate_ds_without_selecting_project(self):
        self.all_datasenders_page.search_with(self.datasender_id_without_web_access)
        self.all_datasenders_page.select_a_data_sender_by_id(self.datasender_id_without_web_access)
        self.all_datasenders_page.perform_datasender_action(ASSOCIATE)
        self.all_datasenders_page.click_confirm()
        self.assertEqual(self.all_datasenders_page.get_error_message(), ERROR_MSG_FOR_NOT_SELECTING_PROJECT)

    @attr('functional_test')
    def test_delete_data_sender(self):
        delete_datasender_id = TestAllDataSenders.register_datasender(DATA_SENDER_TO_DELETE,
                                                                      id=TestAllDataSenders._create_id_for_data_sender())
        self.all_datasenders_page.load()
        self.all_datasenders_page.search_with(delete_datasender_id)
        self.all_datasenders_page.delete_datasender(delete_datasender_id)
        DataSenderDeleteDialog(self.driver).ok()
        self.assertEqual(self.all_datasenders_page.get_delete_success_message(), DELETE_SUCCESS_TEXT)
        self.all_datasenders_page.search_with(delete_datasender_id)
        self.assertFalse(
            self.driver.is_element_present(self.all_datasenders_page.get_checkbox_selector_for_datasender_row(1)))
        self.assertEqual("No matching records found", self.all_datasenders_page.get_empty_table_result())

    @attr('functional_test')
    def test_search(self):
        self.all_datasenders_page.search_with("non_existent_DS")
        self.assertFalse(
            self.driver.is_element_present(self.all_datasenders_page.get_checkbox_selector_for_datasender_row(1)))
        self.assertEqual("No matching records found", self.all_datasenders_page.get_empty_table_result())
        self.assertEqual("0 to 0 of 0 Contact", self.all_datasenders_page.get_pagination_text())
        self.all_datasenders_page.search_with(self.datasender_id_without_web_access)
        self.assertEqual(self.datasender_id_without_web_access,
                         self.all_datasenders_page.get_cell_value(row=1, column=3),
                         msg="matching row does not have specified ID")
        self.assertFalse(
            self.driver.is_element_present(self.all_datasenders_page.get_checkbox_selector_for_datasender_row(2)),
            msg="More than expected number of rows present")
        self.assertEqual("1 to 1 of 1 Contact(s)", self.all_datasenders_page.get_pagination_text())

    @classmethod
    def add_new_user(cls, user_data):
        cls.driver.go_to(ALL_USERS_URL)
        all_users_page = AllUsersPage(cls.driver)
        add_user_page = all_users_page.navigate_to_add_user()
        add_user_page.add_user_with(user_data)
        cls.driver.wait_for_element(UI_TEST_TIMEOUT*2, FLASH_MESSAGE_LABEL, True)
        user_mobile_number = fetch_(MOBILE_PHONE, user_data)
        return user_mobile_number


    @attr('functional_test')
    def test_should_warn_and_not_delete_if_all_ds_selected_are_users(self):
        self.all_datasenders_page.search_with(self.user_ID)
        self.all_datasenders_page.delete_datasender(self.user_ID)
        delete_dialog = UserDeleteDialog(self.driver)
        self.assertRegexpMatches(delete_dialog.get_message(), ALL_DS_TO_DELETE_ARE_USER_MSG)
        delete_dialog.ok()

    @attr('functional_test')
    def test_should_warn_and_delete_only_DS_if_selected_are_users_and_DS(self):
        delete_datasender_id = TestAllDataSenders.register_datasender(DATA_SENDER_TO_DELETE)
        #self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        self.all_datasenders_page.load()
        self.driver.create_screenshot("ds_before_search.png")
        self.all_datasenders_page.search_with(fetch_(FIRST_NAME, NEW_USER_DATA))
        self.all_datasenders_page.click_checkall_checkbox()
        self.driver.create_screenshot("ds_to_delete.png")
        self.all_datasenders_page.perform_datasender_action(DELETE)
        DataSenderDeleteDialog(self.driver).ok()
        self.assertEqual(self.all_datasenders_page.get_delete_success_message(), DELETE_SUCCESS_TEXT)
        self.all_datasenders_page.search_with(self.user_ID)
        self.all_datasenders_page.wait_for_table_to_load()
        self.assertTrue(
             self.driver.is_element_present(self.all_datasenders_page.get_checkbox_selector_for_datasender_row(1)))
        self.all_datasenders_page.search_with(delete_datasender_id)
        self.all_datasenders_page.wait_for_table_to_load()
        self.assertFalse(
            self.driver.is_element_present(self.all_datasenders_page.get_checkbox_selector_for_datasender_row(1)))


    @attr('functional_test')
    def test_should_check_all_checkboxes_when_checking_checkall(self):
        self.all_datasenders_page.click_checkall_checkbox()
        all_ds_count = self.all_datasenders_page.get_datasenders_count()
        all_checked_ds_count = self.all_datasenders_page.get_checked_datasenders_count()
        self.assertEqual(all_ds_count, all_checked_ds_count)

        self.all_datasenders_page.click_checkall_checkbox()
        all_checked_ds_count = self.all_datasenders_page.get_checked_datasenders_count()
        self.assertEqual(all_checked_ds_count, 0)

    @attr("functional_test")
    def test_actions_menu(self):
        self.all_datasenders_page.click_action_button()
        self.assert_action_menu_when_no_datasender_selected()

        self.driver.find(self.all_datasenders_page.get_checkbox_selector_for_datasender_row(1)).click()
        self.all_datasenders_page.click_action_button()
        self.assert_action_menu_shown()
        self.assertFalse(self.all_datasenders_page.is_edit_disabled())
        self.assert_action_menu_when_datasender_selected()

        self.driver.find(self.all_datasenders_page.get_checkbox_selector_for_datasender_row(2)).click()
        self.all_datasenders_page.click_action_button()
        self.assert_action_menu_shown()
        self.assertTrue(self.all_datasenders_page.is_edit_disabled())
        self.assert_action_menu_when_datasender_selected()

    def assert_action_menu_when_datasender_selected(self):
        self.assertFalse(self.all_datasenders_page.is_make_web_user_disabled())
        self.assertFalse(self.all_datasenders_page.is_associate_disabled())
        self.assertFalse(self.all_datasenders_page.is_dissociate_disabled())
        self.assertFalse(self.all_datasenders_page.is_delete_disabled())

    def assert_action_menu_when_no_datasender_selected(self):
        self.assertTrue(self.all_datasenders_page.is_none_selected_shown())
        self.assertEquals("Select a Contact", self.all_datasenders_page.get_none_selected_text())

    def assert_action_menu_shown(self):
        self.assertFalse(self.all_datasenders_page.is_none_selected_shown())

    @attr("functional_test")
    def test_should_check_checkall_when_all_cb_are_checked(self):
        self.all_datasenders_page.click_checkall_checkbox()
        self.assertTrue(self.all_datasenders_page.is_checkall_checked())
        first_row_datasender = self.all_datasenders_page.get_checkbox_selector_for_datasender_row(1)
        self.driver.find(first_row_datasender).click()
        self.assertFalse(self.all_datasenders_page.is_checkall_checked())
        self.driver.find(first_row_datasender).click()
        self.assertTrue(self.all_datasenders_page.is_checkall_checked())

    @attr("functional_test")
    def test_should_show_updated_datasender_details_after_edit(self):
        self.all_datasenders_page.search_with(self.datasender_id_with_web_access)
        self.all_datasenders_page.select_a_data_sender_by_id(self.datasender_id_with_web_access)
        self.all_datasenders_page.select_edit_action()
        AddDataSenderPage(self.driver).enter_data_sender_details_from(EDITED_DATA_SENDER).navigate_to_datasender_page()
        self.all_datasenders_page.wait_for_table_to_load()
        self.all_datasenders_page.search_with(self.datasender_id_with_web_access)
        self.assertEqual(fetch_(NAME, EDITED_DATA_SENDER), self.all_datasenders_page.get_cell_value(1, 2))
        self.assertEqual(self.datasender_id_with_web_access, self.all_datasenders_page.get_cell_value(1, 3))
        location_appended_with_account_location = fetch_(COMMUNE, EDITED_DATA_SENDER) + ",Madagascar"
        self.assertEqual(location_appended_with_account_location, self.all_datasenders_page.get_cell_value(1, 4))
        self.assertEqual(fetch_(GPS, EDITED_DATA_SENDER), self.all_datasenders_page.get_cell_value(1, 5))
        self.assertEqual(fetch_(MOBILE_NUMBER, EDITED_DATA_SENDER), self.all_datasenders_page.get_cell_value(1, 6))


    @attr("functional_test")
    def test_should_give_web_and_smartphone_access(self):
        self.all_datasenders_page.search_with(self.datasender_id_without_web_access)
        self.assertFalse(self.all_datasenders_page.is_web_and_smartphone_device_checkmarks_present(
            self.datasender_id_without_web_access))
        self.all_datasenders_page.select_a_data_sender_by_id(self.datasender_id_without_web_access)
        email_address = fetch_(EMAIL_ADDRESS, VALID_DATASENDER_WITHOUT_WEB_ACCESS)
        self.all_datasenders_page.give_web_and_smartphone_access(email_address)
        self.all_datasenders_page.wait_for_table_to_load()
        self.assertEqual("Access to Web Submission has been given to your DataSenders.",
                         self.all_datasenders_page.get_success_message())
        self.all_datasenders_page.search_with(self.datasender_id_without_web_access)
        self.assertTrue(self.all_datasenders_page.is_web_and_smartphone_device_checkmarks_present(
            self.datasender_id_without_web_access))
        self.assertEqual(email_address, self.all_datasenders_page.get_cell_value(1, 7))

    @attr('functional_test')
    def test_should_not_able_to_use_other_datasender_mobile_number(self):
        self.all_datasenders_page.search_with('rep10')
        self.all_datasenders_page.select_a_data_sender_by_id('rep10')
        self.all_datasenders_page.select_edit_action()
        page = AddDataSenderPage(self.driver)
        page.enter_datasender_mobile_number("1234567890")
        page.click_submit_button()
        time.sleep(2)
        self.assertEqual(page.get_error_message(),
            u'Sorry, the telephone number 1234567890 has already been registered.')

    @attr('functional_test')
    def test_should_update_project_column_of_datasender_when_project_gets_deleted(self):
        global_navigation = GlobalNavigationPage(self.driver)
        dashboard_page = global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()

        create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()
        create_questionnaire_page.create_questionnaire_with(NEW_PROJECT, QUESTIONNAIRE_DATA)

        project_overview_page = create_questionnaire_page.save_and_create_project_successfully()
        project_name = project_overview_page.get_project_title()
        project_id = project_overview_page.get_project_id()

        all_datasender_page = global_navigation.navigate_to_all_data_sender_page()
        all_datasender_page.search_with(self.datasender_id_with_web_access)
        all_datasender_page.select_a_data_sender_by_id(self.datasender_id_with_web_access)
        all_datasender_page.associate_datasender_to_projects(self.datasender_id_with_web_access,[project_name.lower()])
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_id("datasender_table_processing"))

        self.assertIn(project_name.lower(), all_datasender_page.get_project_names(self.datasender_id_with_web_access))

        all_projects_page = global_navigation.navigate_to_view_all_project_page()
        all_projects_page.delete_project(project_name)

        all_datasender_page = global_navigation.navigate_to_all_data_sender_page()
        all_datasender_page.search_with(self.datasender_id_with_web_access)
        all_datasender_page.select_a_data_sender_by_id(self.datasender_id_with_web_access)

        self.assertNotIn(project_name.lower(), all_datasender_page.get_project_names(self.datasender_id_with_web_access))

        #undelete project
        self.driver.go_to(UNDELETE_PROJECT_URL%project_id)
        self.assertIn(project_name.lower(), [elem.text for elem in self.driver.find_elements_(by_css(".project-id-class"))])
        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)

        all_datasender_page.search_with(self.datasender_id_with_web_access)
        all_datasender_page.select_a_data_sender_by_id(self.datasender_id_with_web_access)

        self.assertIn(project_name.lower(), all_datasender_page.get_project_names(self.datasender_id_with_web_access))

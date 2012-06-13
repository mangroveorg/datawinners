# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.common_utils import generateId
from framework.utils.data_fetcher import fetch_, from_
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.alldatasendertests.all_data_sender_data import DATA_SENDER_ID_WITH_WEB_ACCESS
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.projectdatasenderstests.registered_datasenders_data import *


@attr('suit_2')
class ProjectDataSenders(BaseTest):
    def all_projects_page(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        return global_navigation.navigate_to_view_all_project_page()

    @attr('functional_test', 'smoke')
    def test_successfully_giving_web_access_to_newly_registered_data_sender(self):
        """
        Function to test giving web access to newly registered data sender
        """
        data_sender_mobile_number = VALID_DATA_FOR_ADDING_DATASENDER.get(MOBILE_NUMBER)

        all_project_page = self.all_projects_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(VALID_DATA)))
        project_datasenders_page = project_overview_page.navigate_to_datasenders_page()

        add_data_sender_page = project_datasenders_page.navigate_to_add_a_data_sender_page()
        add_data_sender_page.add_data_sender_with(VALID_DATA_FOR_ADDING_DATASENDER)
        self.driver.wait_until_modal_dismissed()

        project_datasenders_page = project_overview_page.navigate_to_datasenders_page()

        self.assertEqual("--", project_datasenders_page.get_data_sender_email_by_mobile_number(data_sender_mobile_number))
        project_datasenders_page.select_a_data_sender_by_mobile_number(data_sender_mobile_number)
        unique_email = "mickey" + generateId() + "@duck.com"

        project_datasenders_page.give_web_access(unique_email)
        self.driver.wait_until_modal_dismissed(10)

        assigned_email = project_datasenders_page.get_data_sender_email_by_mobile_number(data_sender_mobile_number)
        self.assertEqual(unique_email, assigned_email)

        account_page = project_datasenders_page.navigate_to_account_page()
        account_page.select_user_tab()
        self.assertTrue(account_page.is_user_present(unique_email))


    @attr('functional_test', 'smoke')
    def test_show_error_while_giving_web_access_without_selecting_data_sender(self):
        """
        Function to show error while trying to give web access without selecting data sender
        """

        all_project_page = self.all_projects_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(VALID_DATA)))
        project_datasenders_page = project_overview_page.navigate_to_datasenders_page()

        project_datasenders_page.select_web_access_action()

        self.assertEqual(ERROR_MSG_FOR_GIVING_WEB_ACCESS_WITHOUT_SELECTING_DATA_SENDER
            , project_datasenders_page.get_error_message())

    @attr('functional_test')
    def test_registered_data_sender_devices(self):
        all_project_page = self.all_projects_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(VALID_DATA)))
        project_datasenders_page = project_overview_page.navigate_to_datasenders_page()

        devices = project_datasenders_page.get_devices_by_id(DATA_SENDER_ID_WITH_WEB_ACCESS)
        self.assertEquals(devices, "SMS,Web,Smartphone")

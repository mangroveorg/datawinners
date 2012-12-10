# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.common_utils import generateId
from framework.utils.data_fetcher import fetch_, from_
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.alldatasenderstests.all_data_sender_data import DATA_SENDER_ID_WITH_WEB_ACCESS, DATA_SENDER_ID_WITHOUT_WEB_ACCESS
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.projectdatasenderstests.registered_datasenders_data import *
from pages.adddatasenderspage.add_data_senders_locator import REGISTERED_DATASENDERS_LOCATOR


@attr('suit_2')
class ProjectDataSenders(BaseTest):
    def tearDown(self):
        super(ProjectDataSenders, self).tearDown()
        import sys

        exception_info = sys.exc_info()
        if exception_info != (None, None, None):
            import os
            if not os.path.exists("screenshots"):
                os.mkdir("screenshots")
            self.driver.get_screenshot_as_file("screenshots/screenshot-%s-%s.png" % (self.__class__.__name__, self._testMethodName))

    def all_projects_page(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        return global_navigation.navigate_to_view_all_project_page()

    @attr('functional_test', 'smoke')
    def test_successfully_giving_web_access_to_newly_registered_data_sender(self):
        data_sender_mobile_number = VALID_DATA_FOR_ADDING_DATASENDER.get(MOBILE_NUMBER)

        all_project_page = self.all_projects_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(VALID_DATA)))
        project_datasenders_page = project_overview_page.navigate_to_datasenders_page()

        add_data_sender_page = project_datasenders_page.navigate_to_add_a_data_sender_page()
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA_FOR_ADDING_DATASENDER, UNIQUE_ID)
        self.driver.wait_until_modal_dismissed()
        success_message = add_data_sender_page.get_success_message()
        self.assertEqual(success_message, SUCCESS_MSG_ADDED_DS)

        project_datasenders_page = project_overview_page.navigate_to_datasenders_page()

        self.assertEqual("--", project_datasenders_page.get_data_sender_email_by_mobile_number(data_sender_mobile_number))

        project_datasenders_page.select_a_data_sender_by_mobile_number(data_sender_mobile_number)
        unique_email = "mickey" + generateId() + "@duck.com"

        project_datasenders_page.give_web_access(unique_email)
        self.driver.wait_until_modal_dismissed(25)

        assigned_email = project_datasenders_page.get_data_sender_email_by_mobile_number(data_sender_mobile_number)
        self.assertEqual(unique_email, assigned_email)

        account_page = project_datasenders_page.navigate_to_account_page()
        account_page.select_user_tab()
        self.assertFalse(account_page.is_user_present(unique_email))


    @attr('functional_test', 'smoke')
    def test_show_error_while_giving_web_access_without_selecting_data_sender(self):
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

        self.assertTrue(project_datasenders_page.check_sms_device_by_id(DATA_SENDER_ID_WITH_WEB_ACCESS))
        self.assertTrue(project_datasenders_page.check_web_device_by_id(DATA_SENDER_ID_WITH_WEB_ACCESS))
        self.assertTrue(project_datasenders_page.check_smart_phone_device_by_id(DATA_SENDER_ID_WITH_WEB_ACCESS))

        self.assertTrue(project_datasenders_page.check_sms_device_by_id(DATA_SENDER_ID_WITHOUT_WEB_ACCESS))
        self.assertFalse(project_datasenders_page.check_web_device_by_id(DATA_SENDER_ID_WITHOUT_WEB_ACCESS))
        self.assertFalse(project_datasenders_page.check_smart_phone_device_by_id(DATA_SENDER_ID_WITHOUT_WEB_ACCESS))

    def navigate_to_project_datasender_page(self):
        all_project_page = self.all_projects_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(VALID_DATA)))
        return project_overview_page.navigate_to_datasenders_page()

    def check_import_template_filename(self, page):
        import_lightbox = page.open_import_lightbox()
        self.assertEqual(IMPORT_DATA_SENDER_TEMPLATE_FILENAME_EN, import_lightbox.get_template_filename())
        import_lightbox.close_light_box()
        page.switch_language("fr")
        import_lightbox = page.open_import_lightbox()
        self.assertEqual(IMPORT_DATA_SENDER_TEMPLATE_FILENAME_FR, import_lightbox.get_template_filename())
        

    @attr('functional_test', 'smoke')
    def test_the_datasender_template_file_downloaded_on_registered_datasenders_page(self):
        """
        Function to test template file is in correct language
        """
        project_datasenders_page = self.navigate_to_project_datasender_page()
        self.check_import_template_filename(project_datasenders_page)
        

    @attr('functional_test', 'smoke')
    def test_the_datasender_template_file_downloaded_on_add_datasender_page(self):
        """
        Function to test template file is in correct language
        """
        project_datasenders_page = self.navigate_to_project_datasender_page()
        add_data_sender_page = project_datasenders_page.navigate_to_add_a_data_sender_page()
        self.check_import_template_filename(add_data_sender_page)

    @attr('functional_test')
    def test_addition_and_editon(self):
        project_datasenders_page = self.navigate_to_project_datasender_page()
        add_data_sender_page = project_datasenders_page.navigate_to_add_a_data_sender_page()

        add_data_sender_page.enter_data_sender_details_from(VALID_DATASENDER_DATA, "repx01")

        self.assertRegexpMatches(add_data_sender_page.get_success_message(),
                                 fetch_(SUCCESS_MSG, from_(VALID_DATASENDER_DATA)))
        self.driver.wait_until_modal_dismissed(20)
        self.driver.find(REGISTERED_DATASENDERS_LOCATOR).click()
        project_datasenders_page.select_a_data_sender_by_mobile(VALID_DATASENDER_DATA[MOBILE_NUMBER_WITHOUT_HYPHENS])
        project_datasenders_page.select_edit_action()
        add_data_sender_page.enter_data_sender_details_from(VALID_EDIT_DATASENDER_DATA)
        self.assertRegexpMatches(add_data_sender_page.get_success_message(),
            fetch_(SUCCESS_MSG, from_(VALID_EDIT_DATASENDER_DATA)))

    @attr('functional_test')
    def test_addition_with_existing_unique_ID(self):
        project_datasenders_page = self.navigate_to_project_datasender_page()
        add_data_sender_page = project_datasenders_page.navigate_to_add_a_data_sender_page()

        add_data_sender_page.enter_data_sender_details_from(VALID_DATASENDER_DATA_FOR_DUPLICATE_UNIQUE_ID, "repx01")
        error_msg = add_data_sender_page.get_error_message()
        self.assertRegexpMatches(error_msg,
                                 fetch_(ERROR_MSG, from_(VALID_DATASENDER_DATA_FOR_DUPLICATE_UNIQUE_ID)))




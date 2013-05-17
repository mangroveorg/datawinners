from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from nose.plugins.attrib import attr
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.broadcastsmstests.broadcast_sms_data import SMS_VALID_DATA, SMS_EXACT_ON_LIMIT_DATA, \
    ERROR_MESSAGE_MAX_LENGTH_11, ERROR_MESSAGE_MAX_LENGTH_10, MORE_THAN_100_NUMBER
from tests.editprojecttests.edit_project_data import PROJECT_NAME, ACTIVATED_PROJECT_DATA
from tests.logintests.login_data import VALID_CREDENTIALS, NIGERIA_ACCOUNT_CREDENTIAL

@attr('suit_1')
class TestBroadcastSMS(BaseTest):

    @attr('functional_test')
    def test_clear_sms_content_after_send(self):
        send_message_page = self._navigate_to_send_message_page()
        send_message_page.write_sms_content(SMS_VALID_DATA)
        send_message_page.click_send()
        self.assertEquals(send_message_page.get_sms_content(), "")

    @attr('functional_test')
    def test_exceed_sms_content_limitation(self):
        send_message_page = self._navigate_to_send_message_page()
        send_message_page.write_sms_content(SMS_EXACT_ON_LIMIT_DATA + "redundant data")
        self.assertEquals(send_message_page.get_sms_content(), SMS_EXACT_ON_LIMIT_DATA)


    def _navigate_to_send_message_page(self, project_name=None, credential=VALID_CREDENTIALS):
        if project_name is None:
            project_name = fetch_(PROJECT_NAME, from_(ACTIVATED_PROJECT_DATA))
        all_project_page = self._prerequisites_of_edit_project(credential)
        project_overview_page = all_project_page.navigate_to_project_overview_page(project_name)
        send_message_page = project_overview_page.navigate_send_message_tab()
        return send_message_page

    def _prerequisites_of_edit_project(self, credential=VALID_CREDENTIALS):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(credential)
        return global_navigation.navigate_to_view_all_project_page()

    @attr('functional_test')
    def test_should_show_help_text_when_other_people_is_choosen(self):
        send_message_page = self._navigate_to_send_message_page()
        send_message_page.choose_type_other_people("0333333333")
        self.assertTrue(send_message_page.is_other_people_help_text_visible())

    @attr('functional_test')
    def test_should_limit_phone_number_to_11digits_with_nigeria_account(self):
        send_message_page = self._navigate_to_send_message_page(project_name="clinic test project",
            credential=NIGERIA_ACCOUNT_CREDENTIAL)
        self._test_phone_number_length(send_message_page, expected_error_message=ERROR_MESSAGE_MAX_LENGTH_11)


    @attr('functional_test')
    def test_should_limit_phone_number_to_10digits_for_other_organization(self):
        send_message_page = self._navigate_to_send_message_page()
        self._test_phone_number_length(send_message_page)

    def _test_phone_number_length(self, send_message_page, expected_error_message=ERROR_MESSAGE_MAX_LENGTH_10):
        send_message_page.choose_type_other_people(other_numbers="1234567890123")
        send_message_page.click_send()
        error_message = send_message_page.get_other_people_number_error()
        self.assertEqual(error_message, expected_error_message)

    @attr('functional_test')
    def test_should_show_warning_when_people_number_is_more_than_100(self):
        send_message_page = self._navigate_to_send_message_page()
        send_message_page.write_sms_content(SMS_VALID_DATA)
        send_message_page.choose_type_other_people(other_numbers=MORE_THAN_100_NUMBER)
        self.assertFalse(send_message_page.is_warning_shown())
        send_message_page.click_send()
        self.assertTrue(send_message_page.is_warning_shown())


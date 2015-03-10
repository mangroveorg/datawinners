# vim: ai ts=4 sts=4 et sw=4utf-8
import time

from nose.plugins.attrib import attr

from framework.base_test import HeadlessRunnerTest
from framework.utils.data_fetcher import from_, fetch_
from framework.utils.database_manager_postgres import DatabaseManager
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, TRIAL_EXPIRED_PAGE
from tests.logintests.login_data import *
from tests.testsettings import UI_TEST_TIMEOUT
from pages.expiredtrialpage.expired_trial_page import ExpiredTrialPage


class TestLoginPage(HeadlessRunnerTest):
    @attr('functional_test')
    def test_login_with_unactivated_account_credentials(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with(UNACTIVATED_ACCOUNT_CREDENTIALS)
        self.assertEqual(login_page.get_error_message(),
                         fetch_(ERROR_MESSAGE,
                                from_(UNACTIVATED_ACCOUNT_CREDENTIALS)))

    @attr('functional_test')
    def test_login_with_invalid_format_email_address(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with(INVALID_EMAIL_ID_FORMAT)
        self.assertEqual(login_page.get_error_message(),
                         fetch_(ERROR_MESSAGE, from_(INVALID_EMAIL_ID_FORMAT)))

    @attr('functional_test')
    def test_login_with_invalid_password_credential(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with(INVALID_PASSWORD)
        self.assertEqual(login_page.get_error_message(),
                         fetch_(ERROR_MESSAGE, from_(INVALID_PASSWORD)))

    @attr('functional_test')
    def test_login_without_entering_email_address(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with(BLANK_EMAIL_ADDRESS)
        self.assertEqual(login_page.get_error_message(),
                         fetch_(ERROR_MESSAGE, from_(BLANK_EMAIL_ADDRESS)))

    @attr('functional_test')
    def test_login_without_entering_password(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with(BLANK_PASSWORD)
        self.assertEqual(login_page.get_error_message(),
                         fetch_(ERROR_MESSAGE, from_(BLANK_PASSWORD)))

    @attr('functional_test')
    def test_login_without_entering_email_and_password(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with(BLANK_CREDENTIALS)
        self.assertEqual(login_page.get_error_message(), fetch_(ERROR_MESSAGE,
                                                                from_(BLANK_CREDENTIALS)))

    @attr('functional_test')
    def test_register_link_functionality(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        register_page = login_page.navigate_to_registration_page()
        self.driver.wait_for_page_with_title(UI_TEST_TIMEOUT, "Register")
        self.assertEqual(self.driver.get_title(), "Register")

    @attr('functional_test')
    def test_login_with_expired_trial_account(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        dbmanager = DatabaseManager()
        dbmanager.update_active_date_to_expired(EXPIRED_TRIAL_ACCOUNT[USERNAME], 365)
        login_page = LoginPage(self.driver)
        time.sleep(2)
        login_page.login_with(EXPIRED_TRIAL_ACCOUNT)
        
        self.assertEqual(login_page.get_error_message(),
                         fetch_(ERROR_MESSAGE, from_(EXPIRED_TRIAL_ACCOUNT)))


    @attr('functional_test')
    def test_login_with_deactivated_account(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with(DEACTIVATED_ACCOUNT_CREDENTIALS)
        self.assertEqual(login_page.get_error_message(), fetch_(ERROR_MESSAGE,from_(DEACTIVATED_ACCOUNT_CREDENTIALS)))


    @attr('functional_test')
    def test_should_check_trial_expired_page(self):
        self.driver.go_to(TRIAL_EXPIRED_PAGE)
        expired_page = ExpiredTrialPage(self.driver)
        self.assertEqual(expired_page.get_error_message(), TRIAL_EXPIRED_MESSAGE)
        self.assertRegexpMatches(expired_page.get_subscribe_button(), "/en/upgrade/")

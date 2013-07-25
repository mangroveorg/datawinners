# vim: ai ts=4 sts=4 et sw=4utf-8
import time

from nose.plugins.attrib import attr

from framework.base_test import BaseTest
from framework.utils.data_fetcher import from_, fetch_
from framework.utils.database_manager_postgres import DatabaseManager
from pages.expiredtrialpage.expired_trial_page import ExpiredTrialPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import *


@attr('suit_2')
class TestLoginPage(BaseTest):
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
        self.assertEqual(self.driver.get_title(), "Register")

    @attr('functional_test')
    def test_login_with_expired_trial_account(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        dbmanager = DatabaseManager()
        dbmanager.update_active_date_to_expired(EXPIRED_TRIAL_ACCOUNT[USERNAME], 31)
        login_page = LoginPage(self.driver)
        time.sleep(2)
        login_page.login_with(EXPIRED_TRIAL_ACCOUNT)
        expired_trail_account_page = ExpiredTrialPage(self.driver)
        self.assertEqual(expired_trail_account_page.get_error_message(),
                         fetch_(ERROR_MESSAGE, from_(EXPIRED_TRIAL_ACCOUNT)))

        subscribe_button = expired_trail_account_page.get_subscribe_button()
        self.assertEqual("Subscribe Now", subscribe_button[0].text)

    @attr('functional_test')
    def test_login_with_deactivated_account(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with(DEACTIVATED_ACCOUNT_CREDENTIALS)
        self.assertEqual(login_page.get_error_message(), fetch_(ERROR_MESSAGE,from_(DEACTIVATED_ACCOUNT_CREDENTIALS)))

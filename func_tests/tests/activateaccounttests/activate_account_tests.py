# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest

from nose.plugins.attrib import attr

from framework.base_test import setup_driver, teardown_driver, HeadlessRunnerTest
from framework.utils.couch_http_wrapper import CouchHttpWrapper
from pages.activateaccountpage.activate_account_page import ActivateAccountPage
from framework.utils.database_manager_postgres import DatabaseManager
from tests.registrationtests.registration_data import REGISTRATION_SUCCESS_MESSAGE
from tests.registrationtests.registration_tests import register_and_get_email
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, LOGOUT
from tests.logintests.login_data import USERNAME, PASSWORD


class TestActivateAccount(HeadlessRunnerTest):

    @attr('functional_test')
    def test_successful_login_with_uppercased_email(self):
        registration_confirmation_page, self.email = register_and_get_email(self.driver)
        assert REGISTRATION_SUCCESS_MESSAGE == registration_confirmation_page.registration_success_message()
        self.account_activate_page = ActivateAccountPage(self.driver)
        self.postgres_dbmanager = DatabaseManager()
        self.activation_code = self.postgres_dbmanager.get_activation_code(self.email.lower())
        self.account_activate_page.activate_account(self.activation_code)
        self.driver.go_to(LOGOUT)
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        dashboard_page = login_page.do_successful_login_with({USERNAME: self.email.upper(), PASSWORD: u"ngo001"})
        self.assertEqual(dashboard_page.welcome_message(), u"Welcome Mickey Gö!")



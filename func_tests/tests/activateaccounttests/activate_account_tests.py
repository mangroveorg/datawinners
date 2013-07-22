# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from nose.plugins.attrib import attr
from framework.base_test import setup_driver, teardown_driver
from framework.utils.couch_http_wrapper import CouchHttpWrapper
from pages.activateaccountpage.activate_account_page import ActivateAccountPage
from framework.utils.database_manager_postgres import DatabaseManager
from tests.registrationtests.registration_data import REGISTRATION_SUCCESS_MESSAGE
from tests.registrationtests.registration_tests import register_and_get_email
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, LOGOUT
from tests.logintests.login_data import USERNAME, PASSWORD


@attr('suit_1')
class TestActivateAccount(unittest.TestCase):
    _multiprocess_shared_ = True
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        registration_confirmation_page, cls.email = register_and_get_email(cls.driver)
        assert REGISTRATION_SUCCESS_MESSAGE == registration_confirmation_page.registration_success_message()
        cls.account_activate_page = ActivateAccountPage(cls.driver)
        cls.postgres_dbmanager = DatabaseManager()
        cls.activation_code = cls.postgres_dbmanager.get_activation_code(cls.email.lower())
        cls.account_activate_page.activate_account(cls.activation_code)

    @classmethod
    def tearDownClass(cls):
        if cls.email is not None:
            dbmanager = DatabaseManager()
            dbname = dbmanager.delete_organization_all_details(cls.email.lower())
            couchwrapper = CouchHttpWrapper()
            couchwrapper.deleteDb(dbname)
        teardown_driver(cls.driver)

    @attr('functional_test', 'smoke')
    def test_go_to_dashboard_page_after_successful_activation_of_account(self):
        self.assertEqual('Dashboard', self.driver.get_title())

    @attr('functional_test')
    def test_successful_login_with_uppercased_email(self):
        self.driver.go_to(LOGOUT)
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        dashboard_page = login_page.do_successful_login_with({USERNAME: self.email.upper(), PASSWORD: u"ngo001"})
        self.assertEqual(dashboard_page.welcome_message(), u"Welcome Mickey!")



# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.couch_http_wrapper import CouchHttpWrapper
from framework.utils.data_fetcher import fetch_, from_
from tests.activateaccounttests.activate_account_data import *
from pages.activateaccountpage.activate_account_page import ActivateAccountPage
from framework.utils.database_manager_postgres import DatabaseManager
from tests.registrationtests.registration_data import REGISTRATION_SUCCESS_MESSAGE
from tests.registrationtests.registration_tests import register_and_get_email


class TestActivateAccount(BaseTest):

    def setUp(self):
        super(TestActivateAccount, self).setUp()
        registration_confirmation_page, self.email = register_and_get_email(self.driver)
        self.assertEquals(registration_confirmation_page.registration_success_message(), REGISTRATION_SUCCESS_MESSAGE)

        self.account_activate_page = ActivateAccountPage(self.driver)
        self.dbmanager = DatabaseManager()
        self.activation_code = self.dbmanager.get_activation_code(self.email)
        self.account_activate_page.activate_account(self.activation_code)

    def tearDown(self):
        if self.email is not None:
            dbmanager = DatabaseManager()
            dbname = dbmanager.delete_organization_all_details(self.email)
            couchwrapper = CouchHttpWrapper("localhost")
            couchwrapper.deleteDb(dbname)
        super(TestActivateAccount, self).tearDown()

    @attr('functional_test', 'smoke')
    def test_successful_activation_of_account(self):

        self.assertRegexpMatches(self.account_activate_page.get_message(),
                                 fetch_(SUCCESS_MESSAGE, from_(VALID_ACTIVATION_DETAILS)))




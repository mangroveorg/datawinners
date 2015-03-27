from nose.plugins.attrib import attr

from framework.base_test import HeadlessRunnerTest
from framework.utils.database_manager_postgres import DatabaseManager
from pages.activateaccountpage.activate_account_page import ActivateAccountPage
from pages.alldatasenderspage.all_data_senders_page import AllDataSendersPage
from tests.registrationtests.registration_data import REGISTRATION_SUCCESS_MESSAGE
from tests.registrationtests.registration_tests import register_and_get_email


@attr('suit_1')
class TestAllDatasenderBehaviourInTrialOrg(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()

    @attr('functional_test')
    def test_should_show_default_datasender_for_newly_created_datasender(self):
        registration_confirmation_page, self.email = register_and_get_email(self.driver)
        assert REGISTRATION_SUCCESS_MESSAGE == registration_confirmation_page.registration_success_message()
        self.account_activate_page = ActivateAccountPage(self.driver)
        self.postgres_dbmanager = DatabaseManager()
        self.activation_code = self.postgres_dbmanager.get_activation_code(self.email.lower())
        self.account_activate_page.activate_account(self.activation_code)

        
        self.page = AllDataSendersPage(self.driver)
        self.page.load()
        
        all_ds_page = self.page
        self.assertEqual(1, all_ds_page.get_datasenders_count())

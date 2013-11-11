import unittest
import time

from nose.plugins.attrib import attr

from framework.base_test import setup_driver, teardown_driver
from framework.utils.database_manager_postgres import DatabaseManager
from pages.activateaccountpage.activate_account_page import ActivateAccountPage
from testdata.test_data import DATA_WINNER_ALL_DATA_SENDERS_PAGE
from pages.alldatasenderspage.all_data_senders_page import AllDataSendersPage
from tests.registrationtests.registration_data import REGISTRATION_SUCCESS_MESSAGE
from tests.registrationtests.registration_tests import register_and_get_email


@attr('suit_1')
class TestAllDatasenderBehaviourInTrialOrg(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()

        registration_confirmation_page, cls.email = register_and_get_email(cls.driver)
        assert REGISTRATION_SUCCESS_MESSAGE == registration_confirmation_page.registration_success_message()
        cls.account_activate_page = ActivateAccountPage(cls.driver)
        cls.postgres_dbmanager = DatabaseManager()
        cls.activation_code = cls.postgres_dbmanager.get_activation_code(cls.email.lower())
        cls.account_activate_page.activate_account(cls.activation_code)

    def setUp(self):
        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        time.sleep(2)
        self.page = AllDataSendersPage(self.driver)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @attr('functional_test')
    def test_should_show_default_datasender_for_newly_created_datasender(self):
        all_ds_page = self.page
        self.assertEqual(1, all_ds_page.get_datasenders_count())

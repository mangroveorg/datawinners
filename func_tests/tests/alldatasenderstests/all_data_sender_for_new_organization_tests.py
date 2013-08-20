import unittest

from nose.plugins.attrib import attr

from framework.base_test import setup_driver, teardown_driver
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_ALL_DATA_SENDERS_PAGE
from pages.alldatasenderspage.all_data_senders_page import AllDataSendersPage

@attr('suit_1')
class TestAllDataSender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        login_page.do_successful_login_with({"username": "samuel@mailinator.com","password": "samuel"})
        cls.page = AllDataSendersPage(cls.driver)

    def setUp(self):
        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @attr('functional_test')
    def test_should_show_default_datasender_for_newly_created_datasender(self):
        all_ds_page = self.page
        self.assertEqual(1, all_ds_page.get_datasenders_count())

    @attr('functional_test')
    def test_should_disable_associate_and_disassociate_action(self):
        all_ds_page = self.page
        all_ds_page.click_checkall_checkbox()
        self.assertFalse(all_ds_page.is_associate_to_project_action_available())
        self.assertFalse(all_ds_page.is_disassociate_to_project_action_available())
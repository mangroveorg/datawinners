# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time
import unittest
from nose.plugins.attrib import attr
from framework.base_test import setup_driver, teardown_driver
from framework.utils.data_fetcher import fetch_, from_
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.alldatasendertests.all_data_sender_data import *


class TestAllDataSender(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        cls.page = global_navigation.navigate_to_all_data_sender_page()

    def setUp(self):
        self.driver.refresh()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def associate(self, all_data_sender_page):
        all_data_sender_page.select_a_data_sender_by_id(fetch_(UID, from_(ASSOCIATE_DATA_SENDER)))
        all_data_sender_page.associate_data_sender()
        all_data_sender_page.select_project(fetch_(PROJECT_NAME, from_(ASSOCIATE_DATA_SENDER)))
        all_data_sender_page.click_confirm(wait=True)

    @attr('functional_test', 'smoke')
    def test_successful_association_of_data_sender(self):
        """
        Function to test the successful association of DataSender with given project
        """
        all_data_sender_page = self.page
        self.associate(all_data_sender_page)
        self.assertEqual(all_data_sender_page.get_project_names(fetch_(UID, from_(ASSOCIATE_DATA_SENDER))),
                                    fetch_(PROJECT_NAME, from_(ASSOCIATE_DATA_SENDER)))

    @attr('functional_test', 'smoke')
    def test_successful_dissociation_of_data_sender(self):
        """
        Function to test the successful dissociation of DataSender with given project
        """
        all_data_sender_page = self.page
        if all_data_sender_page.get_project_names(fetch_(UID, from_(ASSOCIATE_DATA_SENDER))) == "--":
            self.associate(all_data_sender_page)
        all_data_sender_page.select_a_data_sender_by_id(fetch_(UID, from_(DISSOCIATE_DATA_SENDER)))
        all_data_sender_page.dissociate_data_sender()
        all_data_sender_page.select_project(fetch_(PROJECT_NAME, from_(DISSOCIATE_DATA_SENDER)))
        all_data_sender_page.click_confirm(wait=True)
        self.assertEqual(all_data_sender_page.get_project_names(fetch_(UID, from_(DISSOCIATE_DATA_SENDER))), "--")

    @attr('functional_test')
    def test_dissociate_ds_without_selecting_project(self):
        """
        Function to test the dissociation of DataSender without selecting project
        """
        all_data_sender_page = self.page
        all_data_sender_page.select_a_data_sender_by_id(fetch_(UID, from_(DISSOCIATE_DS_WITHOUT_SELECTING_PROJECT)))
        all_data_sender_page.dissociate_data_sender()
        all_data_sender_page.click_confirm()
        self.assertEqual(all_data_sender_page.get_error_message(), fetch_(ERROR_MSG, from_(DISSOCIATE_DS_WITHOUT_SELECTING_PROJECT)))

    @attr('functional_test')
    def test_associate_ds_without_selecting_project(self):
        """
        Function to test the association of DataSender without selecting project
        """
        all_data_sender_page = self.page
        all_data_sender_page.select_a_data_sender_by_id(fetch_(UID, from_(ASSOCIATE_DS_WITHOUT_SELECTING_PROJECT)))
        all_data_sender_page.associate_data_sender()
        all_data_sender_page.click_confirm()
        self.assertEqual(all_data_sender_page.get_error_message(), fetch_(ERROR_MSG, from_(ASSOCIATE_DS_WITHOUT_SELECTING_PROJECT)))

    @attr('functional_test')
    def test_dissociate_ds_without_selecting_ds(self):
        """
        Function to test the dissociation of DataSender without selecting datasender
        """
        all_data_sender_page = self.page
        all_data_sender_page.dissociate_data_sender()
        self.assertEqual(all_data_sender_page.get_error_message(), fetch_(ERROR_MSG, from_(DISSOCIATE_DS_WITHOUT_SELECTING_DS)))

    @attr('functional_test')
    def test_associate_ds_without_selecting_ds(self):
        """
        Function to test the association of DataSender without selecting datasender
        """
        all_data_sender_page = self.page
        all_data_sender_page.associate_data_sender()
        self.assertEqual(all_data_sender_page.get_error_message(), fetch_(ERROR_MSG, from_(ASSOCIATE_DS_WITHOUT_SELECTING_DS)))

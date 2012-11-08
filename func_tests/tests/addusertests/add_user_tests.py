import unittest
from framework.utils.data_fetcher import fetch_
from framework.base_test import setup_driver, teardown_driver
from nose.plugins.attrib import attr
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS, USERNAME, PASSWORD
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.alluserspage.all_users_page import AllUsersPage
from tests.addusertests.add_user_data import *
from tests.alluserstests.all_users_data import ALL_USERS_URL

@attr('suit_1')
class TestAddUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()

    def setUp(self):
        self.global_navigation = GlobalNavigationPage(self.driver)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def tearDown(self):
        self.global_navigation.sign_out()

    def login(self, credential=VALID_CREDENTIALS):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(credential)

    def prerequest_for_add_user_page(self):
        self.login()
        self.driver.go_to(ALL_USERS_URL)
        all_users_page =  AllUsersPage(self.driver)
        return all_users_page.navigate_to_add_user()

    @attr('functional_test')
    def test_should_add_a_new_user(self):
        add_user_page = self.prerequest_for_add_user_page()
        add_user_page.add_user_with(ADD_USER_DATA)
        message = add_user_page.get_success_message()
        self.assertEqual(message, ADDED_USER_SUCCESS_MSG)
        username = fetch_(USERNAME, ADD_USER_DATA)
        password = DEFAULT_PASSWORD
        new_user_credential = {USERNAME: username, PASSWORD: password}
        self.global_navigation.sign_out()
        self.login(credential=new_user_credential)
        title = self.driver.get_title()
        self.assertEqual(title, DASHBOARD_PAGE_TITLE)
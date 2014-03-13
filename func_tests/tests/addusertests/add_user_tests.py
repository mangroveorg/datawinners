import unittest

from nose.plugins.attrib import attr

from framework.utils.data_fetcher import fetch_
from framework.base_test import setup_driver, teardown_driver, HeadlessRunnerTest
from pages.loginpage.login_page import login
from tests.logintests.login_data import VALID_CREDENTIALS, PASSWORD
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.alluserspage.all_users_page import AllUsersPage
from tests.addusertests.add_user_data import *
from tests.alluserstests.all_users_data import ALL_USERS_URL


@attr('suit_1')
class TestAddUser(HeadlessRunnerTest):
    @attr('functional_test')
    def test_should_add_a_new_user(self):
        self.global_navigation = login(self.driver, VALID_CREDENTIALS)
        self.driver.go_to(ALL_USERS_URL)
        all_users_page = AllUsersPage(self.driver)
        add_user_page = all_users_page.navigate_to_add_user()
        add_user_page.add_user_with(ADD_USER_DATA)
        message = add_user_page.get_success_message()
        self.assertEqual(message, ADDED_USER_SUCCESS_MSG)
        username = fetch_(USERNAME, ADD_USER_DATA)
        password = DEFAULT_PASSWORD
        new_user_credential = {USERNAME: username, PASSWORD: password}
        self.global_navigation.sign_out()
        login(self.driver, new_user_credential)
        title = self.driver.get_title()
        self.assertEqual(title, DASHBOARD_PAGE_TITLE)
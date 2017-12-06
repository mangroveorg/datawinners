import unittest

from nose.plugins.attrib import attr

from framework.utils.data_fetcher import fetch_
from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import by_css
from pages.loginpage.login_page import login
from tests.logintests.login_data import VALID_CREDENTIALS, PASSWORD
from pages.alluserspage.all_users_page import AllUsersPage
from tests.addusertests.add_user_data import *
from tests.alluserstests.all_users_data import ALL_USERS_URL
from time import sleep

class TestAddUser(HeadlessRunnerTest):

    def setUp(self):
        try:
            self.global_navigation.sign_out()
            self.global_navigation = login(self.driver, VALID_CREDENTIALS)
        except:
            self.global_navigation = login(self.driver, VALID_CREDENTIALS)

        self.driver.go_to(ALL_USERS_URL)
        self.all_users_page = AllUsersPage(self.driver)
        self.add_user_page = self.all_users_page.navigate_to_add_user()

    def _create_extended_user(self):
        self.add_user_page.select_role_as_administrator()
        user = generate_user()
        self.add_user_page.add_user_with(user)
        message = self.add_user_page.get_success_message()
        self.assertEqual(message, ADDED_USER_SUCCESS_MSG)
        self.username = fetch_(USERNAME, user)
        password = DEFAULT_PASSWORD
        self.new_user_credential = {USERNAME: self.username, PASSWORD: password}
        self.driver.go_to(ALL_USERS_URL)
        role_for_user = self.all_users_page.get_role_for(self.username)
        self.assertEqual('Administrator', role_for_user, 'Expected role to be Administrator but was %s' % role_for_user)
        self.global_navigation.sign_out()
        login(self.driver, self.new_user_credential)
        title = self.driver.get_title()
        self.assertEqual(title, DASHBOARD_PAGE_TITLE)
        sleep(2)
        self.global_navigation.sign_out()

    @attr('functional_test')
    def test_should_add_a_new_extended_user_as_ngo_admin(self):
        self.add_user_page.select_role_as_administrator()
        user = generate_user()
        self.add_user_page.add_user_with(user)
        message = self.add_user_page.get_success_message()
        self.assertEqual(message, ADDED_USER_SUCCESS_MSG)
        self.username = fetch_(USERNAME, user)
        password = DEFAULT_PASSWORD
        self.new_user_credential = {USERNAME: self.username, PASSWORD: password}
        self.driver.go_to(ALL_USERS_URL)
        role_for_user = self.all_users_page.get_role_for(self.username)
        self.assertEqual('Administrator', role_for_user, 'Expected role to be Administrator but was %s' % role_for_user)
        self.global_navigation.sign_out()
        login(self.driver, self.new_user_credential)
        title = self.driver.get_title()
        self.assertEqual(title, DASHBOARD_PAGE_TITLE)
        sleep(2)
        self.global_navigation.sign_out()

    @attr('functional_test')
    def test_should_add_a_new_project_manager_as_ngo_admin(self):
        self.add_user_page.select_role_as_project_manager()
        questionnaires = self.add_user_page.select_questionnaires(2)
        user = generate_user()
        self.add_user_page.add_user_with(user)
        message = self.add_user_page.get_success_message()
        self.assertEqual(message, ADDED_USER_SUCCESS_MSG)
        self.username = fetch_(USERNAME, user)
        password = DEFAULT_PASSWORD
        self.new_user_credential = {USERNAME: self.username, PASSWORD: password}
        self.driver.go_to(ALL_USERS_URL)
        questionnaire_list_for_user = self.all_users_page.get_questionnaire_list_for(self.username)
        role_for_user = self.all_users_page.get_role_for(self.username)
        self.assertEqual('Project Manager', role_for_user,
                         'Expected role to be Project Manager but was %s' % role_for_user)
        self.assertTrue(questionnaires[0] in questionnaire_list_for_user)
        self.assertTrue(questionnaires[1] in questionnaire_list_for_user)
        self.assertEqual(2, len(questionnaire_list_for_user),
                         'Expected the questionnaires length to be 2 but was %s' %
                         len(questionnaire_list_for_user))
        self.global_navigation.sign_out()
        login(self.driver, self.new_user_credential)
        title = self.driver.get_title()
        self.assertEqual(title, DASHBOARD_PAGE_TITLE)
        sleep(2)
        self.global_navigation.sign_out()

    @attr('functional_test')
    @unittest.skip('Waiting for a fix...')
    def test_should_add_a_new_project_manager_as_extended_user(self):
        self.add_user_page.select_role_as_administrator()
        user = generate_user()
        self.add_user_page.add_user_with(user)
        message = self.add_user_page.get_success_message()
        self.assertEqual(message, ADDED_USER_SUCCESS_MSG)
        self.username = fetch_(USERNAME, user)
        password = DEFAULT_PASSWORD
        self.new_user_credential = {USERNAME: self.username, PASSWORD: password}
        self.global_navigation.sign_out()
        login(self.driver, self.new_user_credential)
        title = self.driver.get_title()
        self.assertEqual(title, DASHBOARD_PAGE_TITLE)
        self.driver.go_to(ALL_USERS_URL)
        self.all_users_page = AllUsersPage(self.driver)
        self.add_user_page = self.all_users_page.navigate_to_add_user()
        self.assertFalse(self.add_user_page.is_administrator_role_visible(),
                         'Expected Administrator Role not to be present but it was present')
        questionnaires = self.add_user_page.select_questionnaires(2)
        user = generate_user()
        self.add_user_page.add_user_with(user)
        message = self.add_user_page.get_success_message()
        self.assertEqual(message, ADDED_USER_SUCCESS_MSG)
        self.username = fetch_(USERNAME, user)
        password = DEFAULT_PASSWORD
        self.new_user_credential = {USERNAME: self.username, PASSWORD: password}
        self.driver.go_to(ALL_USERS_URL)
        questionnaire_list_for_user = self.all_users_page.get_questionnaire_list_for(self.username)
        role_for_user = self.all_users_page.get_role_for(self.username)
        self.assertEqual('Project Manager', role_for_user,
                         'Expected role to be Project Manager but was %s' % role_for_user)
        self.assertTrue(questionnaires[0] in questionnaire_list_for_user)
        self.assertTrue(questionnaires[1] in questionnaire_list_for_user)
        self.assertEqual(2, len(questionnaire_list_for_user),
                         'Expected the questionnaires length to be 2 but was %s' %
                         len(questionnaire_list_for_user))
        self.global_navigation.sign_out()
        login(self.driver, self.new_user_credential)
        title = self.driver.get_title()
        self.assertEqual(title, DASHBOARD_PAGE_TITLE)
        sleep(2)
        self.global_navigation.sign_out()

    @attr('functional_test')
    def test_should_check_when_adding_user_with_existing_username(self):
        user = get_existing_username_user()
        self._validate_and_check_error_message(user,
                                               u'This email address is already in use. Please supply a different email address')
        self.global_navigation.sign_out()
        sleep(2)
        self.add_user_page.confirm_leave_page()

    @attr('functional_test')
    def test_should_check_when_adding_user_with_existing_phonenumber(self):
        user = generate_user_with_existing_phone_number()
        self._validate_and_check_error_message(user,
                                               u'This phone number is already in use. Please supply a different phone number')
        self.global_navigation.sign_out()
        sleep(2)
        self.add_user_page.confirm_leave_page()

    @attr('functional_test')
    def test_should_check_choose_a_role_when_adding_user(self):
        user = generate_user()
        self.add_user_page.add_user_with(user)
        message = self.add_user_page.get_error_messages()
        self.assertEqual(message, "This field is required.")
        self.global_navigation.sign_out()
        sleep(2)
        self.add_user_page.confirm_leave_page()

    @attr('functional_test')
    def test_should_check_when_adding_user_with_invalid_phonenumber(self):
        user = generate_user()
        user.update({MOBILE_PHONE: 'abcdefgh'})
        self._validate_and_check_error_message(user,
                                               u'Invalid phone number')
        self.global_navigation.sign_out()
        sleep(2)
        self.add_user_page.confirm_leave_page()

    @attr('functional_test')
    def test_should_check_when_adding_user_with_invalid_email_address(self):
        user = generate_user()
        user.update({USERNAME: 'abcdefgh'})
        self._validate_and_check_error_message(user,
                                               u'Enter a valid email address. Example:name@organization.com')
        self.global_navigation.sign_out()
        sleep(2)
        self.add_user_page.confirm_leave_page()

    def _validate_and_check_error_message(self, user, expected_message):
        self.add_user_page.select_role_as_project_manager()
        self.add_user_page.add_user_with(user)
        message = self.add_user_page.get_error_messages()
        self.assertEqual(message, expected_message)

    @attr('functional_test')
    @unittest.skip('Failed only in jenkins - Temporarily skipping')
    def test_should_show_warning_when_trying_to_leave_page_without_saving(self):
        user = generate_user()
        self.add_user_page.select_questionnaires()
        self.add_user_page.add_user_with(user, click_submit=False)
        self.driver.refresh()
        expected_msg = u'This page is asking you to confirm that you want to leave - data you have entered may not be saved.'

        alert = self.driver.switch_to_alert()
        self.assertEqual(alert.text, expected_msg)
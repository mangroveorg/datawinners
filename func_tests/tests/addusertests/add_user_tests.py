from nose.plugins.attrib import attr

from framework.utils.data_fetcher import fetch_
from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import by_css
from pages.loginpage.login_page import login
from tests.logintests.login_data import VALID_CREDENTIALS, PASSWORD
from pages.alluserspage.all_users_page import AllUsersPage
from tests.addusertests.add_user_data import *
from tests.alluserstests.all_users_data import ALL_USERS_URL

class TestAddUser(HeadlessRunnerTest):

    def setUp(self):
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

    @attr('functional_test')
    def test_should_add_a_new_extended_user_as_ngo_admin(self):
        self._create_extended_user()

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

    @attr('functional_test')
    def test_should_add_a_new_project_manager_as_extended_user(self):
        self._create_extended_user()
        self.driver.go_to(ALL_USERS_URL)
        self.all_users_page = AllUsersPage(self.driver)
        self.add_user_page = self.all_users_page.navigate_to_add_user()
        self.assertFalse(self.add_user_page.is_administrator_role_visible(), 'Expected Administrator Role not to be present but it was present')
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

    def tearDown(self):
        self.global_navigation.sign_out()


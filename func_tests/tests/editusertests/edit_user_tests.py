from nose.plugins.attrib import attr

from framework.utils.data_fetcher import fetch_
from framework.base_test import HeadlessRunnerTest
from pages.loginpage.login_page import login
from tests.logintests.login_data import VALID_CREDENTIALS, PASSWORD
from pages.alluserspage.all_users_page import AllUsersPage
from tests.editusertests.edit_user_data import *
from tests.addusertests.add_user_data import *
from tests.alluserstests.all_users_data import ALL_USERS_URL


class TestEditUser(HeadlessRunnerTest):
    @attr('functional_test')
    def test_should_edit_an_extended_user_as_ngo_admin(self):
        self.global_navigation = login(self.driver, VALID_CREDENTIALS)
        self.driver.go_to(ALL_USERS_URL)
        all_users_page = AllUsersPage(self.driver)
        add_user_page = all_users_page.navigate_to_add_user()
        user = generate_user()
        add_user_page.select_role_as_administrator()
        add_user_page.add_user_with(user)
        message = add_user_page.get_success_message()
        username = fetch_(USERNAME, user)
        self.driver.go_to(ALL_USERS_URL)
        all_users_page.select_user_with_username(username)
        edit_user_page = all_users_page.select_edit_action()
        self.assertTrue(edit_user_page.is_user_name_text_box_disabled())
        self.assertTrue(edit_user_page.is_user_name_is_prefetched(username))
        self.assertTrue(edit_user_page.is_role_administrator())
        edit_user_page.save_changes({
            "mobile_phone": random_number(9)
        })
        success_message = edit_user_page.get_success_message()
        self.assertEqual(USER_EDITED_SUCCESS_MESSAGE, success_message,
                         'Expected "User has been updated successfully" message but was not found')

    @attr('functional_test')
    def test_should_edit_a_project_manager_as_ngo_admin(self):
        self.global_navigation = login(self.driver, VALID_CREDENTIALS)
        self.driver.go_to(ALL_USERS_URL)
        all_users_page = AllUsersPage(self.driver)
        add_user_page = all_users_page.navigate_to_add_user()
        user = generate_user()
        add_user_page.select_role_as_project_manager()
        add_user_page.select_questionnaires(2, 4)
        add_user_page.add_user_with(user)
        username = fetch_(USERNAME, user)
        self.driver.go_to(ALL_USERS_URL)
        questionnaire_list_for_user = all_users_page.get_questionnaire_list_for(username)
        all_users_page.select_user_with_username(username)
        edit_user_page = all_users_page.select_edit_action()
        self.assertTrue(edit_user_page.is_user_name_text_box_disabled(), 'User name text was expected to be disabled ')
        self.assertTrue(edit_user_page.is_user_name_is_prefetched(username))
        self.assertTrue(edit_user_page.is_role_project_manager())
        self.assertTrue(edit_user_page.are_questionnaires_preselected(questionnaire_list_for_user))
        selected_questionnaires = edit_user_page.select_questionnaires(3)
        edit_user_page.save_changes({
            "mobile_phone": random_number(9),
            "full_name": 'New User Name'
        })
        success_message = edit_user_page.get_success_message()
        self.assertEqual(USER_EDITED_SUCCESS_MESSAGE, success_message,
                         'Expected "User has been updated successfully" message but was not found')

        self.driver.go_to(ALL_USERS_URL)
        self.assertEqual('New User Name', all_users_page.get_full_name_for(username))
        self.assertEqual(3, len(selected_questionnaires),
                         'Expected the questionnaires length to be 3 but was %s' %
                         len(selected_questionnaires))
        self.global_navigation.sign_out()

    @attr('functional_test')
    def test_should_edit_a_project_manager_as_extended_user(self):
        user = generate_user()
        new_user = generate_user()

        # create extended user
        self._create_extended_user(user)
        username = fetch_(USERNAME, user)
        password = DEFAULT_PASSWORD
        extended_user_credentials = {USERNAME: username, PASSWORD: password}
        self.global_navigation.sign_out()

        # Login with extended user and create project manager
        login(self.driver, extended_user_credentials)
        self.driver.go_to(ALL_USERS_URL)

        self.all_users_page = AllUsersPage(self.driver)
        self.assertEqual(0, self.all_users_page.number_of_editable_users_for_role('Administrator'),
                         'Expected Administrators to be non-editable but was editable')
        self.assertEqual(0, self.all_users_page.number_of_editable_users_for_role('Super Admin'),
                         'Expected Super Admin to be non-editable but was editable')
        self.add_user_page = self.all_users_page.navigate_to_add_user()
        self.add_user_page.select_role_as_project_manager()
        self.add_user_page.select_questionnaires(2)
        self.add_user_page.add_user_with(new_user)

        username = fetch_(USERNAME, new_user)
        self.driver.go_to(ALL_USERS_URL)
        self.assertGreater(1, self.all_users_page.number_of_editable_users_for_role('Super Admin'),
                           'Expected Super Admin to be non-editable but was editable')
        self.assertTrue(self.all_users_page.is_editable(username),
                        '%s user was expected to be editable but was not editable')
        questionnaire_list_for_user = self.all_users_page.get_questionnaire_list_for(username)
        self.all_users_page.select_user_with_username(username)
        edit_user_page = self.all_users_page.select_edit_action()
        self.assertTrue(edit_user_page.is_user_name_text_box_disabled(), 'User name text was expected to be disabled ')
        self.assertTrue(edit_user_page.is_user_name_is_prefetched(username))
        self.assertTrue(edit_user_page.is_role_project_manager())
        self.assertTrue(edit_user_page.are_questionnaires_preselected(questionnaire_list_for_user))
        selected_questionnaires = edit_user_page.select_questionnaires(3)
        edit_user_page.save_changes({
            "mobile_phone": random_number(9),
            "full_name": 'New User Name'
        })
        success_message = edit_user_page.get_success_message()
        self.assertEqual(USER_EDITED_SUCCESS_MESSAGE, success_message,
                         'Expected "User has been updated successfully" message but was not found')

        self.driver.go_to(ALL_USERS_URL)
        self.assertEqual('New User Name', self.all_users_page.get_full_name_for(username))
        self.assertEqual(3, len(selected_questionnaires),
                         'Expected the questionnaires length to be 3 but was %s' %
                         len(selected_questionnaires))
        self.global_navigation.sign_out()

    def _create_extended_user(self, user):
        self.global_navigation = login(self.driver, VALID_CREDENTIALS)
        self.driver.go_to(ALL_USERS_URL)
        self.all_users_page = AllUsersPage(self.driver)
        self.add_user_page = self.all_users_page.navigate_to_add_user()
        self.add_user_page.select_role_as_administrator()
        self.add_user_page.add_user_with(user)

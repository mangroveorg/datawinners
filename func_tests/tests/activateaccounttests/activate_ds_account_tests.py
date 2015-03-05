# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from nose.plugins.attrib import attr
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.http import int_to_base36

from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import generate_random_email_id
from pages.loginpage.login_page import LoginPage
from pages.resetpasswordpage.reset_password_page import ResetPasswordPage
from testdata.constants import SUCCESS_MSG
from tests.activateaccounttests.activate_account_data import DS_ACTIVATION_URL, NEW_PASSWORD, VALID_DATASENDER
from testdata.test_data import url, DATA_WINNER_LOGIN_PAGE, LOGOUT
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.testsettings import UI_TEST_TIMEOUT


class TestActivateDSAccount(HeadlessRunnerTest):

    # @attr('functional_test')
    # def test_create_and_activate_datasender(self):
    #     self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
    #     login_page = LoginPage(self.driver)
    #     global_navigation_page = login_page.do_successful_login_with(VALID_CREDENTIALS)
    #     add_datasender_page = global_navigation_page.navigate_to_all_data_sender_page().navigate_to_add_a_data_sender_page()
    #     email = generate_random_email_id()
    #     add_datasender_page.enter_data_sender_details_from(VALID_DATASENDER, email=email)
    #     self.assertIn(VALID_DATASENDER[SUCCESS_MSG], add_datasender_page.get_success_message())
    #     self.driver.go_to(LOGOUT)
    #
    #     user = User.objects.get(username=email)
    #     token = default_token_generator.make_token(user)
    #     self.driver.go_to(url(DS_ACTIVATION_URL % (int_to_base36(user.id), token)))
    #     activation_page = ResetPasswordPage(self.driver)
    #     activation_page.type_same_password(NEW_PASSWORD)
    #     activation_page.click_submit()
    #     self.driver.wait_for_page_with_title(UI_TEST_TIMEOUT, "Data Submission")
    #     self.assertEqual(self.driver.get_title(), "Data Submission")

    @attr('functional_test')
    def test_create_and_activate_datasender(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation_page = login_page.do_successful_login_with(VALID_CREDENTIALS)
        add_datasender_page = global_navigation_page.navigate_to_all_data_sender_page().navigate_to_add_a_data_sender_page()
        email = generate_random_email_id()
        add_datasender_page.enter_data_sender_details_from(VALID_DATASENDER, email=email)
        success_message = add_datasender_page.get_success_message()
        self.assertIn(VALID_DATASENDER[SUCCESS_MSG], success_message)
        rep_id = add_datasender_page.get_rep_id_from_success_message(success_message)
        add_datasender_page.close_add_datasender_dialog()
        all_datasender_page =  global_navigation_page.navigate_to_all_data_sender_page()
        all_datasender_page.associate_datasender_to_projects(rep_id, ["clinic test project1"])
        self.driver.go_to(LOGOUT)

        user = User.objects.get(username=email)
        token = default_token_generator.make_token(user)
        self.driver.go_to(url(DS_ACTIVATION_URL % (int_to_base36(user.id), token)))
        activation_page = ResetPasswordPage(self.driver)
        activation_page.type_same_password(NEW_PASSWORD)
        activation_page.click_submit()
        self.driver.wait_for_page_with_title(UI_TEST_TIMEOUT, "Data Submission")
        self.assertEqual(self.driver.get_title(), "Data Submission")


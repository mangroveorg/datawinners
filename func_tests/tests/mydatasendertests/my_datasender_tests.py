from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import int_to_base36
from framework.base_test import HeadlessRunnerTest
from nose.plugins.attrib import attr
from framework.utils.common_utils import generate_random_email_id
from pages.datasenderactivationpage.activate_datasender_page import DataSenderActivationPage
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import login
from pages.resetpasswordpage.reset_password_page import ResetPasswordPage
from testdata.constants import SUCCESS_MSG
from testdata.test_data import LOGOUT, url
from tests.activateaccounttests.activate_account_data import DS_ACTIVATION_URL
from tests.mydatasendertests.my_datasender_data import VALID_DATASENDER, NEW_PASSWORD
from tests.testsettings import UI_TEST_TIMEOUT


class TestMyDatasenders(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        login(cls.driver)
        global_navigation_page = GlobalNavigationPage(cls.driver)
        cls.all_data_page = global_navigation_page.navigate_to_all_data_page()

        # @attr('functional_test')

    # def test_create_and_activate_datasender(self):
    # self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
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

    @attr('functional_tests')
    def test_registration_of_datasender(self):
        project_data_sender_page = self.all_data_page.navigate_to_my_data_senders_page('clinic2 test project')
        email = generate_random_email_id()
        add_data_sender_page = project_data_sender_page.navigate_to_add_a_data_sender_page()\
            .enter_data_sender_details_from(VALID_DATASENDER, email=email)
        self.assertIn(VALID_DATASENDER[SUCCESS_MSG], add_data_sender_page.get_success_message())
        add_data_sender_page.close_add_datasender_dialog()
        self.driver.go_to(LOGOUT)
        DataSenderActivationPage(self.driver).activate_datasender(email, NEW_PASSWORD)
        self.driver.wait_for_page_with_title(UI_TEST_TIMEOUT, "Data Submission")
        self.assertEqual(self.driver.get_title(), "Data Submission")

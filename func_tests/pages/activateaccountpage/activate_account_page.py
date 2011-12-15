# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.loginpage.login_page import LoginPage
from pages.page import Page
from pages.activateaccountpage.activate_account_locator import *
from testdata.test_data import DATA_WINNER_ACTIVATE_ACCOUNT


class ActivateAccountPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def activate_account(self, activation_code):
        """
        Function to activate account with activation code
         .
        Args:
        'activation_code' is activation code for the account

        Return self
        """
        self.driver.go_to(DATA_WINNER_ACTIVATE_ACCOUNT + activation_code)
        return self

    def get_message(self):
        """
        Function to fetch the message from label of the Activate account page
        page

        Return error message
        """
        return self.driver.find(MESSAGE_LABEL).text

    def go_to_login_page(self):
        """
        Function to go on login page using login link of the Activate account page
        page

        Return login page
        """
        self.driver.find(LOGIN_LINK).click()
        return LoginPage(self.driver)

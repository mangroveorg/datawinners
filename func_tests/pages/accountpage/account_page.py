# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.accountpage.account_locator import *
from pages.page import Page
from pages.alluserspage.all_users_page import AllUsersPage


class AccountPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)


    def select_user_tab(self):
        self.driver.find(USER_TAB).click()
        return AllUsersPage(self.driver)

    def is_user_present(self, user_email):
        all_user_email_tds = self.driver.find_elements_(DATASENDER_USER)
        for td in all_user_email_tds:
            if td.text == user_email:
                return True
        return False


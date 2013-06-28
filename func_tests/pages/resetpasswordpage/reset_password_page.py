# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.page import Page
from pages.resetpasswordpage.reset_password_locator import *


class ResetPasswordPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def click_submit(self):
        self.driver.find(SUBMIT_BUTTON).click()

    def type_same_password(self, new_password):
        self.driver.find_text_box(NEW_PASSWORD_LOCATOR).enter_text(new_password)
        self.driver.find_text_box(PASSWORD_CONFIRM_LOCATOR).enter_text(new_password)
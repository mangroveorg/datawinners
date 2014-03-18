# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from framework.utils.common_utils import CommonUtilities
from pages.page import Page

from pages.registerconfirmationpage.registration_confirmation_locator import *
from tests.testsettings import UI_TEST_TIMEOUT


class RegistrationConfirmationPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def registration_success_message(self):
        com_util = CommonUtilities(self.driver)
        com_util.wait_for_element(UI_TEST_TIMEOUT, WELCOME_MESSAGE_LI)
        success_message = self.driver.find(WELCOME_MESSAGE_LI).text
        return success_message

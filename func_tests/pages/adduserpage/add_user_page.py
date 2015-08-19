# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from pages.page import Page
from framework.utils.common_utils import by_css
from pages.adddatasenderspage.add_data_senders_locator import FLASH_MESSAGE_LABEL
from tests.testsettings import UI_TEST_TIMEOUT


class AddUserPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def add_user_with(self, user_data):
        for key, value in user_data.items():
            self.driver.find_text_box(by_css("input[name=%s]" % key)).enter_text(value)
        self.driver.find(by_css("button[id=submit]")).click()

    def get_success_message(self):
        locator = self.driver.wait_for_element(UI_TEST_TIMEOUT * 2, FLASH_MESSAGE_LABEL, True)
        return locator.text

    def select_role_as_administrator(self):
        self.driver.find(by_css("input[id=option_administrator]")).click()

    def select_role_as_project_manager(self):
        self.driver.find(by_css("input[id=option_project_manager]")).click()

    def select_questionnaires(self, no_of_questionnaires=0):
        for index in range(0, no_of_questionnaires):
            self.driver.wait_for_element(10,
                                         by_css(".questionnaire-list ul li:nth-child(%s) input[type=checkbox]" % (index+1)),
                                         True).click()
        return [
            self.driver.wait_for_element(10, by_css(".questionnaire-list ul li:nth-child(1) span"), True).text,
            self.driver.wait_for_element(10, by_css(".questionnaire-list ul li:nth-child(2) span"), True).text
        ]

    def is_administrator_role_visible(self):
        return self.driver.is_element_present(by_css("input[id=option_administrator]"))

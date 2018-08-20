# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from pages.page import Page
from framework.utils.common_utils import by_css
from pages.adddatasenderspage.add_data_senders_locator import FLASH_MESSAGE_LABEL
from pages.adduserpage.add_user_locator import *
from tests.testsettings import UI_TEST_TIMEOUT
from time import sleep


class AddUserPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def add_user_with(self, user_data, click_submit=True):
        for key, value in user_data.items():
            self.driver.find_text_box(by_css("input[name='%s']" % key)).enter_text(value)
        if click_submit:
            sleep(2)
            self.driver.find(by_css("button[id=submit]")).click()
            self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT * 2, by_css(".loading"))
        sleep(2)
        self.driver.wait_for_page_load()

    def get_success_message(self):
        locator = self.driver.wait_for_element(UI_TEST_TIMEOUT * 2, FLASH_MESSAGE_LABEL, True)
        return locator.text

    def select_role_as_administrator(self):
        self.driver.find(by_css("input[id=option_administrator]")).click()

    def select_role_as_project_manager(self):
        self.driver.find(by_css("input[id=option_project_manager]")).click()

    def select_questionnaires(self, no_of_questionnaires=0, from_index=0):
        self._uncheck_all_questionnaires()
        for index in range(from_index, (from_index+no_of_questionnaires)):
            self.driver.wait_for_element(10,
                                         by_css(".questionnaire-list ul li:nth-child(%s) input[type=checkbox]" % (index+1)),
                                         True).click()
        list_of_questionnaires = []
        for index in range(0, no_of_questionnaires):
            element = self.driver.wait_for_element(10,
                                                   by_css(".questionnaire-list ul li:nth-child(%s) span" % (index + 1)),
                                                   True)
            list_of_questionnaires.append(element.text)
        return list_of_questionnaires

    def is_administrator_role_visible(self):
        return self.driver.is_element_present(by_css("input[id=option_administrator]"))

    def _uncheck_all_questionnaires(self):
        selected_questionnaires = self.driver.find_elements_by_css_selector('.questionnaire-list ul li input:checked')
        for element in selected_questionnaires:
            element.click()

    def get_error_messages(self):
        locator = self.driver.wait_for_element(UI_TEST_TIMEOUT * 2, ERROR_MESSAGES_LOCATOR, True)
        return locator.text

    def confirm_leave_page(self):
        locator = self.driver.find(CONFIRM_LEAVE_PAGE_BUTTON)
        if locator.is_displayed():
            locator.click()

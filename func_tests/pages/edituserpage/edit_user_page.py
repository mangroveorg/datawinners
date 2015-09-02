# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from selenium.common.exceptions import InvalidElementStateException
from pages.adduserpage.add_user_locator import ERROR_MESSAGES_LOCATOR, CONFIRM_LEAVE_PAGE_BUTTON

from pages.page import Page
from framework.utils.common_utils import by_css, by_xpath
from pages.adddatasenderspage.add_data_senders_locator import FLASH_MESSAGE_LABEL
from tests.testsettings import UI_TEST_TIMEOUT


class EditUserPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def save_changes(self, user_data=None):
        if not user_data:
            user_data = {}
        self.edit_values(user_data)
        self.driver.find(by_css("button[id=submit]")).click()

    def edit_values(self, user_data):
        for key, value in user_data.items():
            self.driver.find_text_box(by_css("input[name=%s]" % key)).enter_text(value)

    def get_success_message(self):
        locator = self.driver.wait_for_element(UI_TEST_TIMEOUT * 2, FLASH_MESSAGE_LABEL, True)
        return locator.text

    def get_error_messages(self):
        locator = self.driver.wait_for_element(UI_TEST_TIMEOUT * 2, ERROR_MESSAGES_LOCATOR, True)
        return locator.text

    def select_role_as_administrator(self):
        self.driver.find(by_css("input[id=option_administrator]")).click()

    def select_role_as_project_manager(self):
        self.driver.find(by_css("input[id=option_project_manager]")).click()

    def select_questionnaires(self, no_of_questionnaires=0, from_index=0):
        self._uncheck_all_questionnaires()
        for index in range(from_index, from_index+no_of_questionnaires):
            self.driver.wait_for_element(10,
                                         by_css(".questionnaire-list ul li:nth-child(%s) input[type=checkbox]" % (
                                             index + 1)),
                                         True).click()
        list_of_questionnaires = []
        for index in range(0, no_of_questionnaires):
            element = self.driver.wait_for_element(10,
                                                   by_css(".questionnaire-list ul li:nth-child(%s) span" % (index + 1)),
                                                   True)
            list_of_questionnaires.append(element.text)
        return list_of_questionnaires

    def is_user_name_is_prefetched(self, username):
        prefetched_username = self.driver.find(by_css("span[id=prefetched-username]")).text
        return True if prefetched_username == username else False

    def is_role_administrator(self):
        administrator_checked = self.driver.find(by_css("input[id=option_administrator]")).get_attribute('checked')
        return True if administrator_checked is not None else False

    def is_role_project_manager(self):
        project_manager_checked = self.driver.find(by_css("input[id=option_project_manager]")).get_attribute('checked')
        return True if project_manager_checked is not None else False

    def are_questionnaires_preselected(self, questionnaires):
        elements = self.driver.find_elements_by_css_selector('.questionnaire-list ul li input:checked + span')
        preselected_questionnaires = [element.text for element in elements]
        return True if set(questionnaires) == set(preselected_questionnaires) else False

    def _uncheck_all_questionnaires(self):
        selected_questionnaires = self.driver.find_elements_by_css_selector('.questionnaire-list ul li input:checked')
        for element in selected_questionnaires:
            element.click()

    def confirm_leave_page(self):
        locator = self.driver.find(CONFIRM_LEAVE_PAGE_BUTTON)
        if locator.is_displayed():
            locator.click()

    def select_questionnaires_by_name(self, questionnaire_names):
        for name in questionnaire_names:
            self.driver.find(by_xpath("//span[contains(text(), '%s')]/../input" % name)).click()



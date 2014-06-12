# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.allsubjectspage.add_subject_page import AddSubjectPage
from pages.allsubjectspage.all_subjects_locator import *
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT


class AllSubjectsListPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def number_of_rows(self):
        rows = self.driver.find_elements_(by_css("table#subjects_table tbody tr"))
        return len(rows)

    def selected_page_size(self):
        return int(self.driver.get_input_value(by_css("#subjects_table_length select")))

    def set_page_size(self, size=10):
        self.driver.find(by_css("#subjects_table_length select")).find_element_by_xpath(
            "//option[@value=" + str(size) + "]").click()
        self.wait_for_processing()

    def search(self, search_text):
        self.driver.create_screenshot(filename="subject_filter.png")
        search_box = self.driver.find_text_box(by_css("#subjects_table_filter>span>input"))
        search_box.enter_text(search_text)
        self.wait_for_processing()

    def wait_for_processing(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css(".search-loader"))
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".search-loader"))

    def get_row_text(self, row_index):
        return self.driver.find_elements_(by_css("#subjects_table tbody tr"))[row_index].text

    def rows(self):
        return self.driver.find_elements_(by_css("#subjects_table tbody tr"))

    def navigate_to_register_subject_page(self):
        self.driver.find(by_id("register_subjects")).click()
        return AddSubjectPage(self.driver)

    def select_subject_by_id(self, subject_id):
        self.wait_for_processing()
        self.search(subject_id)
        selector = by_css("input[value=%s]" % subject_id)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, selector, True)
        self.driver.find(selector).click()

    def _select_subject_action(self):
        action_buttons = self.driver.find_elements_(by_css(".action"))
        action_buttons[0].click()

    def click_edit_action_button(self):
        for i in range(0,3):
            self._select_subject_action()
            if self._wait_for_element_visible():
                break

        self.driver.find_visible_element(by_css(".edit")).click()
        return AddSubjectPage(self.driver)

    def _wait_for_element_visible(self):
        try:
            self.driver.wait_for_element(1, by_css(".edit"), True)
            return True
        except:
            return False

    def click_delete_action_button(self):
        self._select_subject_action()
        self.driver.find_visible_element(by_css(".delete")).click()

    def get_successfully_deleted_message(self):
        message_element_selector = 'div.success-message-box'
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css(message_element_selector), True)
        return self.driver.find(by_css(message_element_selector)).text

    def is_subject_present(self, subject_id):
        self.wait_for_processing()
        return self.driver.is_element_present(by_css("input[value=%s]" % subject_id))

    def empty_table_text_visible(self):
        return self.driver.find(by_css(".dataTables_empty")).is_displayed()
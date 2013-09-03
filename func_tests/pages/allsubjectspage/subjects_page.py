# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from pages.allsubjectspage.all_subjects_locator import *
from pages.page import Page


class SubjectsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def number_of_rows(self):
        rows = self.driver.find_elements_(by_css("table#subjects_table tbody tr"))
        return len(rows)

    def selected_page_size(self):
        return int(self.driver.get_input_value(by_css("#subjects_table_length select")))

    def set_page_size(self, size=10):
        self.driver.find(by_css("#subjects_table_length select")).find_element_by_xpath("//option[@value=" + str(size) + "]").click()
        self.wait_for_processing()

    def search(self, search_text):
        search_box = self.driver.find_text_box(by_css("#subjects_table_filter>input"))
        search_box.enter_text(search_text)
        self.wait_for_processing()

    def wait_for_processing(self):
        self.driver.wait_for_element(2,by_css(".search-loader"))
        self.driver.wait_until_element_is_not_present(2,by_css(".search-loader"))

    def get_row_text(self, row_index):
        return self.driver.find_elements_(by_css("#subjects_table tbody tr"))[row_index].text

    def rows(self):
        return self.driver.find_elements_(by_css("#subjects_table tbody tr"))

    def click_add_a_subject_type_link(self):
        self.driver.find(by_id("add_new_subject_type")).click()

    def add_entity_type_with(self, entity_type, wait=True):
        """
        Function to enter entity type in the text box and click on the Add button
         .
        Args:
        'entity_data' is entity name

        Return self
        """
        # self.driver.find_text_box({"locator":"id_entity_type_text","by":"By.ID"}).enter_text(entity_type)
        self.driver.find_text_box(by_id("id_entity_type_text")).enter_text(entity_type)
        self.driver.find(by_id("add_type")).click()
        if wait:
            self.driver.wait_until_element_is_not_present(5, by_css("#type_message .ajax_loader"))
        return self

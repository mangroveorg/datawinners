# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time
from pages.dataanalysispage.data_analysis_locator import *
from pages.page import Page
from pages.submissionlogpage.submission_log_page import SubmissionLogPage
from pages.websubmissionpage.web_submission_page import WebSubmissionPage
from tests.dataanalysistests.data_analysis_data import CURRENT_MONTH, LAST_MONTH, YEAR_TO_DATE


class DataAnalysisPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)
        self.date_range_dict = {CURRENT_MONTH: self.select_current_month,
                           LAST_MONTH: self.select_last_month,
                           YEAR_TO_DATE: self.select_year_to_date}

    def navigate_to_all_data_record_page(self):
        """
        Function to navigate all data record page

        Return data all data record
         """
        self.driver.find(ALL_DATA_RECORDS_LINK).click()
        return SubmissionLogPage(self.driver)

    def get_data_from_row(self, row_web_element):
        """
        Function to fetch the data of given row

        Args:
        row_web_element is web element object for the row

        Return row data
        """
        return row_web_element.text

    def get_data_rows(self):
        """
        Function to fetch the number of data rows

        return list of web elements
        """
        return self.driver.find_elements_(DATA_ROWS)

    def get_question(self, question_number):
        """
        Function to fetch the question text of given question number

        Args:
        question_number is question number

        Return question text
        """
        return self.driver.find(by_css(QUESTION_LABEL_CSS % (question_number + 1))).text

    def get_all_data_records(self):
        """
        Function to fetch the data of all the available rows

        Args:
        row_web_element is web element object for the row

        Return list of data
        """
        rows = self.get_data_rows()
        data_record_list = []
        for row_web_element in rows:
            data_record_list.append(self.get_data_from_row(row_web_element))
        return data_record_list

    def get_all_data_records_from_multiple_pages(self):
        data_record_list = []
        while True:
            data_record_list.extend(self.get_all_data_records())
            if self.driver.is_element_present(NEXT_BUTTON_DISABLED) :
                break
            self.go_to_next_page()
        return data_record_list

    def get_number_of_rows(self):
        """
        Function to get the number of data records

        Return number of rows
        """
        return self.get_data_rows().__len__()

    def get_all_question_labels(self):
        """
        Function to get all the questions

        Return list of web element
        """
        return self.driver.find_elements_(QUESTION_LABELS)

    def get_number_of_questions(self):
        """
        Function to get the number of questions

        Return number of questions
        """
        return self.get_data_rows().__len__()
    
    def get_all_questions(self):
        """
        Function to get all the questions

        Return list of web element
        """
        question_labels = self.get_all_question_labels()
        questions = []
        for question_label in question_labels[1:]:
            questions.append(unicode(question_label.text))
        return questions

    def select_current_month(self):
        """
        Function to select the date range from the drop down
        """
        self.driver.find_text_box(DATE_RANGE_PICKER_TB).click()
        self.driver.find(CURRENT_MONTH_LABEL).click()

    def select_last_month(self):
        """
        Function to select the date range from the drop down
        """
        self.driver.find_text_box(DATE_RANGE_PICKER_TB).click()
        self.driver.find(LAST_MONTH_LABEL).click()

    def select_year_to_date(self):
        """
        Function to select the date range from the drop down
        """
        self.driver.find_text_box(DATE_RANGE_PICKER_TB).click()
        self.driver.find(YEAR_TO_DATE_LABEL).click()

    def filter_data(self):
        """
        Function to filter the data according to date range
        """
        self.driver.find(FILTER_BUTTON).click()
        self.driver.wait_until_element_is_not_present(20, LOADING_GIF)

    def go_to_next_page(self):
        """
        Function to navigate on next data records page
        """
        self.driver.find(NEXT_BUTTON).click()

    def navigate_to_web_submission_tab(self):
        self.driver.find(by_css('.secondary_tab>li:nth-child(4) a')).click()
        return WebSubmissionPage(self.driver)

    def select_page_size(self, size_str="10"):
        self.driver.find_drop_down(PAGE_SIZE_SELECT).set_selected(size_str)
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time
import datetime

from pages.dataanalysispage.data_analysis_locator import *
from pages.page import Page
from pages.submissionlogpage.submission_log_page import SubmissionLogPage
from pages.websubmissionpage.web_submission_page import WebSubmissionPage
from tests.dataanalysistests.data_analysis_data import CURRENT_MONTH, LAST_MONTH, YEAR_TO_DATE, DAILY_DATE_RANGE, MONTHLY_DATE_RANGE


class DataAnalysisPage(SubmissionLogPage):
    def __init__(self, driver):
        super(DataAnalysisPage, self).__init__(driver)

    def get_number_of_columns(self, row):
        row = row+1 #to ignore hidden row for select all msg
        columns = self.driver.find_elements_(by_xpath(".//*[@class='submission_table']/tbody/tr[%s]/td" % row))
        return len(columns)

    def get_all_data_on_nth_row(self, row):
        row_data = []
        time.sleep(2)
        column_count = self.get_number_of_columns(row)
        if column_count == 1:
            return self.get_empty_datatable_text()
        for col in range(1, column_count + 1):
            row_data.append(self.get_cell_value(row, col))
        return row_data

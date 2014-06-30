# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from string import lower
from framework.utils.common_utils import by_xpath, by_css
import pages
from pages.alldatapage.all_data_locator import *
from pages.dataanalysispage.data_analysis_page import DataAnalysisPage
from pages.page import Page
from pages.submissionlogpage.submission_log_page import SubmissionLogPage
from pages.websubmissionpage.web_submission_page import WebSubmissionPage
from framework.utils.common_utils import CommonUtilities


class AllDataPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def navigate_to_submission_log_page(self, project_name):
        """
        Function to navigate to all data records page of the website

        Return All Data Records page
         """
        self.driver.find(by_xpath(All_DATA_RECORDS_LINK_XPATH % lower(project_name))).click()
        return SubmissionLogPage(self.driver)

    def navigate_to_data_analysis_page(self, project_name):
        """
        Function to navigate to data analysis page of the website

        Return Data Analysis page
         """
        self.driver.find(by_xpath(ANALYSIS_LINK_XPATH % project_name)).click()
        return DataAnalysisPage(self.driver)

    def navigate_to_web_submission_page(self, project_name):
        self.driver.find(by_xpath(WEB_SUBMISSION_LINK_XPATH % project_name)).click()
        return WebSubmissionPage(self.driver)

    def has_all_failed_submission_link(self):
        comm_util = CommonUtilities(self.driver)
        if comm_util.is_element_present(by_css(ALL_FAILED_SUBMISSION_LINK)):
            return True
        return False

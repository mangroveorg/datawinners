# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import from_, fetch_
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.dataanalysistests.data_analysis_data import *
from tests.logintests.login_data import VALID_CREDENTIALS

@attr('suit_1')
class TestDataAnalysis(BaseTest):
    def prerequisites_of_data_analysis(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        all_data_page = global_navigation.navigate_to_all_data_page()
        return all_data_page.navigate_to_data_analysis_page(fetch_(PROJECT_NAME, from_(DEFAULT_DATA_FOR_QUESTIONNAIRE)))

    @attr('functional_test', 'smoke')
    def test_questions_in_table_header(self):
        """
        Function to test the questions shown in the data analysis table
        """
        data_analysis_page = self.prerequisites_of_data_analysis()
        questions = fetch_(HEADERS, from_(DEFAULT_DATA_FOR_ANALYSIS))
        self.assertEquals(questions, data_analysis_page.get_all_questions())

    @attr('functional_test', 'smoke')
    def test_data_records_in_table(self):
        """
        Function to test the data records shown in the data analysis table
        """
        data_analysis_page = self.prerequisites_of_data_analysis()
        data_analysis_page.select_page_size()
        records = data_analysis_page.get_all_data_records()
        print records
        self.assertEquals(fetch_(DATA_RECORDS, from_(DEFAULT_DATA_FOR_ANALYSIS)),
            records)

    @unittest.skip("JiaFeng will fix it on #1364")
    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_current_month(self):
        """
        Function to test the data records filtering
        """
        data_analysis_page = self.prerequisites_of_data_analysis()
        data_analysis_page.date_range_dict[fetch_(DATE_RANGE, from_(FILTER_BY_CURRENT_MONTH))]()
        data_analysis_page.filter_data()
        self.assertEquals(fetch_(DATA_RECORDS, from_(FILTER_BY_CURRENT_MONTH)),
                          data_analysis_page.get_all_data_records())

    @unittest.skip("JiaFeng will fix it on #1364")
    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_last_month(self):
        """
        Function to test the data records filtering
        """
        data_analysis_page = self.prerequisites_of_data_analysis()
        data_analysis_page.date_range_dict[fetch_(DATE_RANGE, from_(FILTER_BY_LAST_MONTH))]()
        data_analysis_page.filter_data()
        self.assertEquals(fetch_(DATA_RECORDS, from_(FILTER_BY_LAST_MONTH)),
                          data_analysis_page.get_all_data_records())

    @unittest.skip("JiaFeng will fix it on #1364")
    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_year_to_date(self):
        """
        Function to test the data records filtering
        """
        data_analysis_page = self.prerequisites_of_data_analysis()
        data_analysis_page.date_range_dict[fetch_(DATE_RANGE, from_(FILTER_BY_YEAR_TO_DATE))]()
        data_analysis_page.filter_data()
        self.assertEquals(fetch_(DATA_RECORDS, from_(FILTER_BY_YEAR_TO_DATE)), data_analysis_page.get_all_data_records_from_multiple_pages())

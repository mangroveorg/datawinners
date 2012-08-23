# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from nose.plugins.attrib import attr
import time
from framework.base_test import BaseTest, setup_driver, teardown_driver
from framework.utils.data_fetcher import from_, fetch_
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.dataanalysistests.data_analysis_data import *
from tests.logintests.login_data import VALID_CREDENTIALS

@attr('suit_1')
class TestDataAnalysis(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.data_analysis_page = cls.prerequisites_of_data_analysis()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def setUp(self):pass

    def tearDown(self):pass

    @classmethod
    def prerequisites_of_data_analysis(cls):
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        all_data_page = global_navigation.navigate_to_all_data_page()
        return all_data_page.navigate_to_data_analysis_page(fetch_(PROJECT_NAME, from_(DEFAULT_DATA_FOR_QUESTIONNAIRE)))

    @attr('functional_test', 'smoke')
    def test_questions_in_table_header(self):
        questions = fetch_(HEADERS, from_(DEFAULT_DATA_FOR_ANALYSIS))
        self.assertEquals(questions, self.data_analysis_page.get_all_questions())

    @attr('functional_test', 'smoke')
    def test_should_return_data_records_in_table(self):
        self.data_analysis_page.select_page_size()
        records = self.data_analysis_page.get_all_data_records()
        self.assertIsNotNone(records)

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_current_month(self):
        self.verify_reporting_period_filter(FILTER_BY_CURRENT_MONTH)

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_last_month(self):
        self.verify_reporting_period_filter(FILTER_BY_LAST_MONTH)

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_year_to_date(self):
        self.verify_reporting_period_filter(FILTER_BY_YEAR_TO_DATE)

    def verify_reporting_period_filter(self, period):
        data_analysis_page = self.data_analysis_page
        data_analysis_page.date_range_dict[fetch_(DATE_RANGE, from_(period))]()
        time.sleep(1)
        data_analysis_page.filter_data()
        data_records = data_analysis_page.get_all_data_records()
        report_period = [datetime.strptime(record.split(' ')[1], '%d.%m.%Y') for record in data_records]
        current_month_period = data_analysis_page.get_reporting_period().split(' - ')
        report_period_start, report_period_end = current_month_period[0], current_month_period[-1]
        self.assertTrue(report_period_start <= each <= report_period_end for each in report_period)

# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from unittest.case import SkipTest
from nose.plugins.attrib import attr
import time
from framework.base_test import BaseTest, setup_driver, teardown_driver
from framework.utils.data_fetcher import from_, fetch_
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.dataanalysistests.data_analysis_data import *
from tests.logintests.login_data import VALID_CREDENTIALS

SUBMISSION_DATE_FORMAT = '%d.%m.%Y'
MONTHLY_REPORTING_PERIOD_FORMAT = "%m.%Y"

@attr('suit_1')
class TestDataAnalysis(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.global_navigation = cls.prerequisites_of_data_analysis()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def setUp(self):pass

    def tearDown(self):pass

    @classmethod
    def go_to_analysis_page(cls, project_name = fetch_(PROJECT_NAME, from_(DEFAULT_DATA_FOR_QUESTIONNAIRE))):
        all_data_page = cls.global_navigation.navigate_to_all_data_page()
        return all_data_page.navigate_to_data_analysis_page(project_name)

    @classmethod
    def prerequisites_of_data_analysis(cls):
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        return global_navigation

    @attr('functional_test', 'smoke')
    def test_questions_in_table_header(self):
        analysis_page = self.go_to_analysis_page()
        questions = fetch_(HEADERS, from_(DEFAULT_DATA_FOR_ANALYSIS))
        self.assertEquals(questions, analysis_page.get_all_questions())

    @attr('functional_test', 'smoke')
    def test_should_return_data_records_in_table(self):

        analysis_page = self.go_to_analysis_page()
        analysis_page.select_page_size()
        records = analysis_page.get_all_data_records()
        self.assertIsNotNone(records)

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_current_month(self):
        self.verify_reporting_period_filter(FILTER_BY_CURRENT_MONTH, self.go_to_analysis_page())

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_last_month(self):
        self.verify_reporting_period_filter(FILTER_BY_LAST_MONTH, self.go_to_analysis_page())

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_year_to_date(self):
        self.verify_reporting_period_filter(FILTER_BY_YEAR_TO_DATE, self.go_to_analysis_page())

    def _to_date_list(self, data_records, date_format):
        return [datetime.strptime(record, date_format) for record in data_records]

    def assert_in_date_range(self, range, data_records, date_format=SUBMISSION_DATE_FORMAT):
        range = self._to_date_list(range, date_format)
        self.assertTrue(all([range[0] <= each <= range[-1] for each in self._to_date_list(data_records, date_format)]))

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_date_range_with_monthly_reporting_period(self):
        data_analysis_page = self.go_to_analysis_page("Clinic Test Project With Monthly Reporting Period".lower())
        data_analysis_page.open_reporting_period_drop_down()
        data_analysis_page.date_range_dict[MONTHLY_DATE_RANGE]()
        start_year = datetime.today().year - 1
        start_month = datetime.today().month
        end_year = datetime.today().year
        end_month = datetime.today().month
        data_analysis_page.select_month_range(start_year, start_month, end_year, end_month)
        time.sleep(1)
        data_analysis_page.click_go_button()
        report_period = data_analysis_page.get_all_data_records_by_column(1)
        current_month_period = data_analysis_page.get_reporting_period().split(' - ')
        self.assert_in_date_range(current_month_period, report_period, MONTHLY_REPORTING_PERIOD_FORMAT)

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_date_range_with_daily_reporting_period(self):
        data_analysis_page = self.go_to_analysis_page()
        data_analysis_page.open_reporting_period_drop_down()
        data_analysis_page.date_range_dict[DAILY_DATE_RANGE]()
        start_year = datetime.today().year - 1
        day = datetime.today().day
        month = datetime.today().month
        end_date = datetime.today()
        time.sleep(1)
        data_analysis_page.select_date_range(start_year, month, day, end_date.year, end_date.month, end_date.day)
        time.sleep(1)
        data_analysis_page.click_go_button()
        report_period = data_analysis_page.get_all_data_records_by_column(1)
        current_month_period = data_analysis_page.get_reporting_period().split(' - ')
        self.assert_in_date_range(current_month_period, report_period)

    def verify_reporting_period_filter(self, period, data_analysis_page):
        data_analysis_page.open_reporting_period_drop_down()
        data_analysis_page.date_range_dict[fetch_(DAILY_DATE_RANGE, from_(period))]()
        time.sleep(1)
        data_analysis_page.click_go_button()
        report_period = data_analysis_page.get_all_data_records_by_column(1)
        period = data_analysis_page.get_reporting_period().split(' - ')
        self.assert_in_date_range(period, report_period)

    def verify_submission_date_filter(self, period, data_analysis_page):
        data_analysis_page.open_submission_date_drop_down()
        data_analysis_page.date_range_dict[period]()
        time.sleep(1)
        data_analysis_page.click_go_button()
        submission_date = data_analysis_page.get_all_data_records_by_column(2)
        period = data_analysis_page.get_submission_date().split(' - ')
        self.assert_in_date_range(period, submission_date)

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_subject_filter(self):
        data_analysis_page = self.go_to_analysis_page()
        subject_name = 'ANALAMANGA'
        data_analysis_page.select_for_subject_type(subject_name)
        data_analysis_page.click_go_button()
        data_records = data_analysis_page.get_all_data_records()
        subject_names = [record.split(' ')[0] for record in data_records]
        subject_sets = set(subject_names)
        self.assertEqual(1, len(subject_sets))
        self.assertEqual(subject_name, subject_names[0])

    def verify_filter_by_data_sender(self, data_sender, project_name = fetch_(PROJECT_NAME, from_(DEFAULT_DATA_FOR_QUESTIONNAIRE))):
        data_analysis_page = self.go_to_analysis_page(project_name)
        data_analysis_page.select_for_data_sender(data_sender[-1])
        data_analysis_page.click_go_button()
        data_records = data_analysis_page.get_all_data_records_by_column(3)
        data_senders_set = set(data_records)
        self.assertEqual(1, len(data_senders_set))
        str_data_sender = data_sender[0] + ' ' + data_sender[1]
        self.assertEqual(str_data_sender.strip(), data_records[0])

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_admin(self):
        self.verify_filter_by_data_sender(('Tester Pune', 'admin', 'tester150411@gmail.com'))

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_sms_or_web_data_sender(self):
        self.verify_filter_by_data_sender(('Shweta', 'rep1', '1234567890'))

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_test_data_sender(self):
        self.verify_filter_by_data_sender(('TEST', '', 'TEST'), 'Clinic Test Project With Monthly Reporting Period'.lower())

    @attr('functional_test')
    def test_should_close_daterange_dropdown_when_opening_subject_dropdown(self):
        data_analysis_page = self.go_to_analysis_page()
        data_analysis_page.open_reporting_period_drop_down()
        time.sleep(1)
        self.assertTrue(data_analysis_page.daterange_drop_down_is_opened())
        data_analysis_page.open_subject_type_drop_down()
        time.sleep(1)
        self.assertFalse(data_analysis_page.daterange_drop_down_is_opened())

    @attr('functional_test')
    def test_should_close_subject_dropdown_when_opening_daterange_dropdown(self):
        data_analysis_page = self.go_to_analysis_page('Clinic Test Project With Monthly Reporting Period'.lower())
        self.assertFalse(data_analysis_page.dropdown_checklist_is_opened())
        data_analysis_page.open_subject_type_drop_down()
        self.assertTrue(data_analysis_page.dropdown_checklist_is_opened())
        data_analysis_page.open_reporting_period_drop_down()
        time.sleep(1)
        self.assertTrue(data_analysis_page.daterange_drop_down_is_opened())
        self.assertFalse(data_analysis_page.dropdown_checklist_is_opened())

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_submission_date_within_current_month(self):
        self.verify_submission_date_filter(CURRENT_MONTH, self.go_to_analysis_page())

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_submission_date_within_last_month(self):
        self.verify_submission_date_filter(LAST_MONTH, self.go_to_analysis_page())

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_submission_date_within_year_to_date(self):
        self.verify_submission_date_filter(YEAR_TO_DATE, self.go_to_analysis_page())

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_keyword(self):
        analysis_page = self.go_to_analysis_page()
        keyword = "Neurological "
        analysis_page.input_keyword(keyword)
        analysis_page.click_go_button()
        filtered_data = analysis_page.get_all_data_records_by_column(7)
        self.assertEqual(len(filtered_data), 25)
        self.assertTrue(all([keyword in item for item in filtered_data]))

    @attr('functional_test', 'smoke')
    def test_should_clear_checked_item_in_drodown_list_when_click_clear_link(self):
        subject_names = ["ANALAMANGA", "Analalava"]
        analysis_page = self.go_to_analysis_page()
        default_text = analysis_page.get_dropdown_control_text()
        [analysis_page.select_for_subject_type(name) for name in subject_names]
        analysis_page.open_subject_type_drop_down()

        self.assertEquals(', '.join(subject_names), analysis_page.get_dropdown_control_text())

        analysis_page.clear_dropdown()

        self.assertEquals(default_text, analysis_page.get_dropdown_control_text())


    @attr('functional_test', 'smoke')
    def test_should_keep_dropdown_list_opened_when_click_clear_link(self):
        analysis_page = self.go_to_analysis_page()
        analysis_page.open_subject_type_drop_down()
        analysis_page.clear_dropdown()
        
        self.assertTrue(analysis_page.dropdown_checklist_is_opened())






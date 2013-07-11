# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import copy
import time

from nose.plugins.attrib import attr

from framework.base_test import BaseTest, setup_driver, teardown_driver
from framework.utils.data_fetcher import from_, fetch_
from pages.dataanalysispage.data_analysis_page import DataAnalysisPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.dataanalysistests.data_analysis_data import *
from tests.logintests.login_data import VALID_CREDENTIALS


SUBMISSION_DATE_FORMAT = "%b. %d, %Y, %I:%M %p"
DD_MM_YYYY_FORMAT = '%d.%m.%Y'

MONTHLY_REPORTING_PERIOD_FORMAT = "%m.%Y"


@attr('suit_1')
class TestDataAnalysis(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.URL = None
        cls.driver = setup_driver()
        cls.global_navigation = cls.prerequisites_of_data_analysis()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def go_to_analysis_page(cls, project_name=fetch_(PROJECT_NAME, from_(DEFAULT_DATA_FOR_QUESTIONNAIRE))):
        all_data_page = cls.global_navigation.navigate_to_all_data_page()
        analysis_page = all_data_page.navigate_to_data_analysis_page(project_name)
        if not cls.URL:
            cls.URL = cls.driver.current_url
        return analysis_page


    @classmethod
    def prerequisites_of_data_analysis(cls):
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        return global_navigation

    def get_analysis_page(self):
        if self.URL:
            self.driver.go_to(self.URL)
            self.driver.wait_for_page_with_title(time_out_in_seconds=10, title='Data Analysis')
            analysis_page = DataAnalysisPage(self.driver)
        else:
            analysis_page = self.go_to_analysis_page()
        return analysis_page

    @attr('functional_test', 'smoke')
    def test_data_analysis_page(self):
        analysis_page = self.get_analysis_page()
        questions = fetch_(HEADERS, from_(DEFAULT_DATA_FOR_ANALYSIS))
        self.assertEquals(questions, analysis_page.get_all_questions())
        analysis_page.select_page_size()
        self.assertIsNotNone(analysis_page.get_all_data_records())


    @attr('functional_test', 'smoke')
    def test_filter_data_records(self):
        data_analysis_page = self.get_analysis_page()
        self.verify_reporting_period_filter(data_analysis_page, FILTER_BY_CURRENT_MONTH)
        self.verify_reporting_period_filter(data_analysis_page, FILTER_BY_LAST_MONTH)
        self.verify_reporting_period_filter(data_analysis_page, FILTER_BY_YEAR_TO_DATE)

        self.verify_submission_date_filter(data_analysis_page, CURRENT_MONTH)
        self.verify_submission_date_filter(data_analysis_page, LAST_MONTH)
        self.verify_submission_date_filter(data_analysis_page, YEAR_TO_DATE)

        self.verify_filter_data_records_by_subject_filter(data_analysis_page)


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
        self.assert_in_date_range(current_month_period, report_period, range_format=MONTHLY_REPORTING_PERIOD_FORMAT,
                                  date_format=MONTHLY_REPORTING_PERIOD_FORMAT)

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_date_range_with_daily_reporting_period(self):
        data_analysis_page = self.get_analysis_page()
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

    @attr('functional_test')
    def test_should_update_text_when_selecting_subjects(self):
        data_analysis_page = self.get_analysis_page()
        subjects = ['ANALAMANGA', 'Andapa', "Antsirabe"]
        data_analysis_page.select_for_subject_type(subjects[0])
        data_analysis_page.select_for_subject_type(subjects[1])
        subject_text = data_analysis_page.get_subject_filter_caption()
        self.assertEqual(subject_text, 'ANALAMANGA, Andapa')
        data_analysis_page.select_for_subject_type(subjects[2])
        subject_text = data_analysis_page.get_subject_filter_caption()
        self.assertEqual(subject_text, 'ANALAMANGA, Andapa, Antsirabe')

    def verify_filter_data_records_by_subject_filter(self, data_analysis_page):
        subject = ('ANALAMANGA', 'cli11')
        data_analysis_page.select_for_subject_type(subject[0])
        data_analysis_page.click_go_button()
        subject_names = data_analysis_page.get_all_data_records_by_column(0)
        subject_sets = set(subject_names)
        self.assertEqual(1, len(subject_sets))
        self.assertEqual(subject[0] + subject[1], subject_names[0])

    def verify_filter_by_data_sender(self, data_analysis_page, data_sender):
        data_analysis_page.select_for_data_sender(data_sender[-1])
        data_analysis_page.click_go_button()
        data_records = data_analysis_page.get_all_data_records_by_column(3)
        data_senders_set = set(data_records)
        self.assertEqual(1, len(data_senders_set))
        str_data_sender = data_sender[0] + data_sender[1]
        self.assertEqual(str_data_sender.strip(), data_records[0])

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_datasender(self):
        data_analysis_page = self.go_to_analysis_page(fetch_(PROJECT_NAME, from_(DEFAULT_DATA_FOR_QUESTIONNAIRE)))
        self.verify_filter_by_data_sender(data_analysis_page, ('Tester Pune', 'rep12'))
        self.verify_filter_by_data_sender(data_analysis_page, ('Shweta', 'rep1'))

    @attr('functional_test')
    def test_daterange_dropdown_and_subject_dropdown_should_toggle_when_opened(self):
        data_analysis_page = self.get_analysis_page()

        data_analysis_page.open_subject_type_drop_down()
        self.assertTrue(data_analysis_page.dropdown_checklist_is_opened())
        self.assertFalse(data_analysis_page.daterange_drop_down_is_opened())

        data_analysis_page.open_reporting_period_drop_down()
        time.sleep(1)
        self.assertTrue(data_analysis_page.daterange_drop_down_is_opened())
        self.assertFalse(data_analysis_page.dropdown_checklist_is_opened())

        data_analysis_page.open_subject_type_drop_down()
        time.sleep(1)
        self.assertTrue(data_analysis_page.dropdown_checklist_is_opened())
        self.assertFalse(data_analysis_page.daterange_drop_down_is_opened())

    @attr('functional_test', 'smoke')
    def test_filter_data_records_by_keyword(self):
        analysis_page = self.get_analysis_page()
        keyword = "Neurological "
        analysis_page.input_keyword(keyword)
        analysis_page.click_go_button()
        filtered_data = analysis_page.get_all_data_records_by_column(7)
        self.assertEqual(len(filtered_data), 10)
        self.assertTrue(all([keyword in item for item in filtered_data]))


    @attr('functional_test')
    def test_should_sort_data_in_alphanumerical_order_except_for_submission_date(self):
        analysis_page = self.go_to_analysis_page(project_name="test data sorting")
        default = analysis_page.get_all_data_records_by_column(4)
        expected_default = ["12.2012", "20, 34", "-12, 34", "12, 34", "cat, dog", "2012.01.14", "cat", "456", "123",
                            "12.23.2011", "2011.12.12"]
        self.assertEqual(default, expected_default)
        self.sort_data_by_word_question(analysis_page)
        self.sort_data_by_mc_question(analysis_page)
        self.sort_data_by_gps_question(analysis_page)
        self.sort_data_by_date_question(analysis_page)
        self.sort_data_by_submission_date(analysis_page)

    def verify_reporting_period_filter(self, data_analysis_page, period):
        data_analysis_page.open_reporting_period_drop_down()
        data_analysis_page.date_range_dict[fetch_(DAILY_DATE_RANGE, from_(period))]()
        time.sleep(1)
        data_analysis_page.click_go_button()
        report_period = data_analysis_page.get_all_data_records_by_column(1)
        period = data_analysis_page.get_reporting_period().split(' - ')
        self.assert_in_date_range(period, report_period)

    def verify_submission_date_filter(self, data_analysis_page, period):
        data_analysis_page.open_submission_date_drop_down()
        data_analysis_page.date_range_dict[period]()
        time.sleep(1)
        data_analysis_page.click_go_button()
        submission_date = data_analysis_page.get_all_data_records_by_column(2)
        period = data_analysis_page.get_submission_date().split(' - ')
        #This is specifically put in here as on the 1st of a month when we choose 'Current Month' we dont get date as
        # date1-date2 it comes as just date1
        if len(period) == 1:
            period.append(copy.deepcopy(period[0]))
        self.assert_in_date_range(period, submission_date, date_format=SUBMISSION_DATE_FORMAT)

    def assert_in_date_range(self, range, data_records, range_format=DD_MM_YYYY_FORMAT, date_format=DD_MM_YYYY_FORMAT):
        range = self._to_date_list(range, range_format)
        if date_format == SUBMISSION_DATE_FORMAT and range_format == DD_MM_YYYY_FORMAT:
            range[-1] = range[-1].replace(hour=23, minute=59)
        self.assertTrue(all([range[0] <= each <= range[-1] for each in self._to_date_list(data_records, date_format)]))

    def _to_date_list(self, data_records, date_format):
        return [datetime.strptime(record, date_format) for record in data_records]


    def sort_data_by_word_question(self, analysis_page):
        analysis_page.click_column_header_to_change_order(5)
        expected_ordered = ["-12, 34", "12, 34", "12.2012", "12.23.2011", "123", "20, 34", "2011.12.12", "2012.01.14",
                            "456", "cat", "cat, dog"]
        ordered = analysis_page.get_all_data_records_by_column(4)
        self.assertEqual(ordered, expected_ordered)

    def sort_data_by_mc_question(self, analysis_page):
        analysis_page.click_column_header_to_change_order(6)
        expected_ordered = ["AB", "AB", "B+", "B+", "B+", "B+", "O+", "O+", "O+", "O-", "O-"]
        ordered = analysis_page.get_all_data_records_by_column(5)
        self.assertEqual(ordered, expected_ordered)

    def sort_data_by_gps_question(self, analysis_page):
        analysis_page.click_column_header_to_change_order(7)
        expected_ordered = ["10.12,11.13", "11.23,17.66", "12,14", "16.34,11.26", "16.34,11.76", "21.16,14.3", "39,14",
                            "5.10,50.12", "56.34,11.00", "61.10,58.99", "65.24,28.45"]
        ordered = analysis_page.get_all_data_records_by_column(6)
        self.assertEqual(ordered, expected_ordered)

    def sort_data_by_date_question(self, analysis_page):
        analysis_page.click_column_header_to_change_order(2)
        expected_ordered = ["11.03.2010", "04.09.2010", "25.12.2010", "15.01.2011", "25.01.2011", "20.02.2011",
                            "25.06.2011", "15.10.2011", "10.02.2012", "11.06.2012", "25.12.2012"]
        ordered = analysis_page.get_all_data_records_by_column(1)
        self.assertEqual(ordered, expected_ordered)

    def sort_data_by_submission_date(self, analysis_page):
        analysis_page.click_column_header_to_change_order(3)
        expected_ordered = ["2011.12.12", "12.23.2011", "123", "456", "cat", "2012.01.14", "cat, dog", "-12, 34",
                            "12.2012", "12, 34", "20, 34"]
        ordered = analysis_page.get_all_data_records_by_column(4)
        self.assertEqual(', '.join(ordered), ', '.join(expected_ordered))

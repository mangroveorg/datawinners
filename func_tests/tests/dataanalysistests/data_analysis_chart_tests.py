# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time
from datetime import datetime, timedelta
from unittest import SkipTest
from framework.base_test import BaseTest, setup_driver, teardown_driver
from framework.exception import CouldNotLocateElementException
from framework.utils.data_fetcher import fetch_, from_
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.dataanalysistests.data_analysis_data import PROJECT_NAME, DEFAULT_DATA_FOR_QUESTIONNAIRE, DAILY_DATE_RANGE
from tests.dataextractionapitests.data_extraction_api_data import VALID_CREDENTIALS

@SkipTest
class TestDataAnalysisChart(BaseTest):
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

    def _go_to_chart_view(self, project_name = fetch_(PROJECT_NAME, from_(DEFAULT_DATA_FOR_QUESTIONNAIRE))):
        analysis_page = self.go_to_analysis_page(project_name)
        analysis_page.go_to_chart_view()
        return analysis_page;

    def _filter_data_of_today(self, end_date):
        analysis_page = self._go_to_chart_view()
        analysis_page.open_reporting_period_drop_down()
        analysis_page.date_range_dict[DAILY_DATE_RANGE]()
        today = datetime.today()
        analysis_page.select_date_range(today.year, today.month, today.day, end_date.year, end_date.month, end_date.day)
        time.sleep(1)
        analysis_page.click_go_button()
        return analysis_page;

    def test_should_return_chart_info_when_there_are_mc_questions_and_submissions(self):
        expected = "View charts of your multiple choice questions."
        analysis_page = self._go_to_chart_view()
        self.assertEqual(expected,  analysis_page.get_chart_info_2_text())

    def test_should_return_chart_info_when_there_are_mc_questions_and_no_submissions(self):
        expected = u"successful submissions will appear here. Learn More"
        analysis_page = self._go_to_chart_view(project_name="clinic2 test project")
        self.assertTrue(analysis_page.get_chart_info_2_text().find(expected)>=0)

    def test_should_return_chart_info_when_there_are_mc_questions_and_no_submissions_after_filtered(self):
        expected = u"No submissions available for this search. Try changing some of the filters."
        analysis_page = self._filter_data_of_today(end_date=datetime.today()-timedelta(1))
        self.assertEqual(analysis_page.get_chart_info_2_text(),expected)

    def test_should_return_chart_info_when_there_no_mc_questions(self):
        expected = u"You do not have any multiple choice questions (Answer Type: List of choices) to display here."
        analysis_page = self._go_to_chart_view(project_name="clinic test project with monthly reporting period")
        self.assertEqual(analysis_page.get_chart_info_2_text(),expected)



    def test_should_show_pie_chart_and_bar_chart_for_single_choice_questions(self):
        analysis_page = self._go_to_chart_view()
        self._assert_pie_and_bar_visibilities(analysis_page, 0, True)

        analysis_page.show_bar_chart(0)
        self._assert_pie_and_bar_visibilities(analysis_page, 0, False)

        analysis_page.show_pie_chart(0)
        self._assert_pie_and_bar_visibilities(analysis_page, 0, True)

    def test_should_only_show_bar_chart_for_multiple_choice_questions(self):
        analysis_page = self._go_to_chart_view()
        self._assert_pie_and_bar_visibilities(analysis_page, 1, False)

        try:
            analysis_page.show_pie_chart(1)
            self.assertTrue(False)
        except CouldNotLocateElementException as e:
            pass

    def test_show_table(self):
        analysis_page = self._go_to_chart_view()
        self.assertIsNotNone(analysis_page.get_table(0))
        try:
            analysis_page.get_multiple_choice_question_explanation(0)
            self.assertTrue(False)
        except CouldNotLocateElementException as e:
            pass

        self.assertIsNotNone(analysis_page.get_table(1))
        self.assertIsNotNone(analysis_page.get_multiple_choice_question_explanation(1))
        self.assertIsNotNone(analysis_page.get_table(1))
        self.assertIsNotNone(analysis_page.get_multiple_choice_question_explanation(2))

    def _assert_pie_and_bar_visibilities(self, analysis_page, question_index, is_pie_shown):
        pie_chart = analysis_page.get_pie_chart(question_index)
        bar_chart = analysis_page.get_bar_chart(question_index)

        self.assertIsNotNone(pie_chart)
        self.assertIsNotNone(bar_chart)

        if is_pie_shown:
            self.assertTrue(pie_chart.get_attribute('style').find('display: none;') < 0)
            self.assertTrue(bar_chart.get_attribute('style').find('display: none;') >= 0)
        else:
            self.assertTrue(bar_chart.get_attribute('style').find('display: none;') < 0)
            self.assertTrue(pie_chart.get_attribute('style').find('display: none;') >= 0)
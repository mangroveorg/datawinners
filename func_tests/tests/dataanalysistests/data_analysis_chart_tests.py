# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time
from datetime import datetime, timedelta
from unittest import SkipTest
from framework.base_test import BaseTest, setup_driver, teardown_driver, HeadlessRunnerTest
from framework.exception import CouldNotLocateElementException
from framework.utils.common_utils import by_css
from framework.utils.data_fetcher import fetch_, from_
from pages.loginpage.login_page import LoginPage, login
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.dataanalysistests.data_analysis_data import PROJECT_NAME, DEFAULT_DATA_FOR_QUESTIONNAIRE, DAILY_DATE_RANGE, \
    NEW_PROJECT_DATA, QUESTIONNAIRE_DATA, NO_CHART_TEXT, NEW_PROJECT_DATA_WITHOUT_MCQ, QUESTIONNAIRE_DATA_WITHOUT_MCQ, \
    NEW_PROJECT_DATA_SINGLE_CHOICE, QUESTIONNAIRE_DATA_SINGLE_CHOICE, VALID_ANSWERS, QUESTIONNAIRE_DATA_MULTIPLE_CHOICE, \
    NEW_PROJECT_DATA_MULTIPLE_CHOICE, VALID_ANSWERS_MULTIPLE_CHOICE, NEW_PROJECT_DATA_ORDER, QUESTIONNAIRE_DATA_ORDER, \
    VALID_ANSWERS_ORDER
from tests.dataextractionapitests.data_extraction_api_data import VALID_CREDENTIALS
#We will test this when we play any story or fix bugs doing charting
# @SkipTest
class TestDataAnalysisChart(HeadlessRunnerTest):
    @classmethod
    def setUpClass(self):
        HeadlessRunnerTest.setUpClass()
        self.global_navigation_page = login(self.driver)

    @classmethod
    def create_new_project(self, new_project_data, questionnaire_data):
        dashboard = self.global_navigation_page.navigate_to_dashboard_page()
        questionnaire_creation_options_page = dashboard.navigate_to_create_project_page()
        create_questionnaire_page = questionnaire_creation_options_page.select_blank_questionnaire_creation_option()
        create_questionnaire_page.create_questionnaire_with(new_project_data, questionnaire_data)
        create_questionnaire_page.save_and_create_project_successfully()
        self.driver.wait_for_page_with_title(5, 'Questionnaires - Overview')
        return ProjectOverviewPage(self.driver)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @classmethod
    def go_to_analysis_page(cls, project_name = fetch_(PROJECT_NAME, from_(DEFAULT_DATA_FOR_QUESTIONNAIRE))):
        all_data_page = cls.global_navigation_page.navigate_to_all_data_page()
        return all_data_page.navigate_to_data_analysis_page(project_name)

    def _go_to_chart_view(self, project_name = fetch_(PROJECT_NAME, from_(DEFAULT_DATA_FOR_QUESTIONNAIRE))):

        analysis_page = self.go_to_analysis_page(project_name)
        analysis_page.go_to_chart_view()
        return analysis_page

    def _filter_data_of_today(self, end_date):
        analysis_page = self._go_to_chart_view()
        analysis_page.open_reporting_period_drop_down()
        analysis_page.date_range_dict[DAILY_DATE_RANGE]()
        today = datetime.today()
        analysis_page.select_date_range(today.year, today.month, today.day, end_date.year, end_date.month, end_date.day)
        time.sleep(1)
        analysis_page.click_go_button()
        return analysis_page

    def test_should_return_chart_info_when_there_are_mc_questions_and_no_submissions(self):
        expected = u"Once your Data Senders have sent in Submissions, they will appear here."
        project_overview_page = self.create_new_project(NEW_PROJECT_DATA, QUESTIONNAIRE_DATA)
        analysis_page = project_overview_page.navigate_to_data_page()
        analysis_page.go_to_chart_view()
        self.assertEqual(analysis_page.get_no_charts_text(), expected)

    def test_should_return_chart_info_when_there_no_mc_questions(self):
        expected = u'Once your Data Senders have sent in Submissions, they will appear here.'
        project_overview_page = self.create_new_project(NEW_PROJECT_DATA_WITHOUT_MCQ, QUESTIONNAIRE_DATA_WITHOUT_MCQ)
        analysis_page = project_overview_page.navigate_to_data_page()
        analysis_page.go_to_chart_view()
        self.assertEqual(analysis_page.get_no_charts_text(), expected)


    def test_should_show_pie_chart_and_bar_chart_for_single_choice_questions(self):
        project_overview_page = self.create_new_project(NEW_PROJECT_DATA_SINGLE_CHOICE, QUESTIONNAIRE_DATA_SINGLE_CHOICE)
        web_submission_page = project_overview_page.navigate_to_data_page().navigate_to_web_submission_tab()
        web_submission_page.fill_questionnaire_with(VALID_ANSWERS)
        web_submission_page.submit_answers()
        analysis_page = project_overview_page.navigate_to_data_page()
        analysis_page.go_to_chart_view()
        self.assertTrue(analysis_page.is_chart_visible())

    def test_should_return_chart_info_when_there_are_mc_questions_and_submissions(self):
        project_overview_page = self.create_new_project(NEW_PROJECT_DATA_MULTIPLE_CHOICE, QUESTIONNAIRE_DATA_MULTIPLE_CHOICE)
        web_submission_page = project_overview_page.navigate_to_data_page().navigate_to_web_submission_tab()
        web_submission_page.fill_questionnaire_with(VALID_ANSWERS_MULTIPLE_CHOICE)
        web_submission_page.submit_answers()
        analysis_page = project_overview_page.navigate_to_data_page()
        analysis_page.go_to_chart_view()
        self.assertTrue(analysis_page.is_chart_visible())


    def test_should_return_chart_in_the_same_order_as_the_questionnaire_is_created(self):
        project_overview_page = self.create_new_project(NEW_PROJECT_DATA_ORDER, QUESTIONNAIRE_DATA_ORDER)
        web_submission_page = project_overview_page.navigate_to_data_page().navigate_to_web_submission_tab()
        web_submission_page.fill_questionnaire_with(VALID_ANSWERS_ORDER)
        web_submission_page.submit_answers()
        analysis_page = project_overview_page.navigate_to_data_page()
        analysis_page.go_to_chart_view()
        expected_value = ['Testing chart','Testing chart2']
        self.assertEquals(expected_value[0],analysis_page.get_chart_question_title("1"))
        self.assertEquals(expected_value[1],analysis_page.get_chart_question_title("2"))
from nose.plugins.attrib import attr
from framework.base_test import HeadlessRunnerTest, teardown_driver
from pages.loginpage.login_page import LoginPage
from tests.logintests.login_data import VALID_CREDENTIALS
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from pages.page import Page
from tests.dwuniversitytests.dw_university_data import *

class TestDWUniversityHelpContent(HeadlessRunnerTest):

    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        login_page = LoginPage(cls.driver)
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        cls.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        cls.dw_university_page = Page(cls.driver)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @attr('functional_test')
    def test_datawinners_university_for_some_global_urls(self):
        for dw_page_url in DW_PAGES_HAVING_HELP:
            self.driver.go_to(url(dw_page_url))
            self.assertTrue(self.dw_university_page.is_help_content_available())


    @attr('functional_test')
    def test_datawinners_university_project_level(self):
        overview_page = self._navigate_to_overview_page()
        self._verify_datawinners_university()
        overview_page.navigate_to_questionnaire_tab()
        self._verify_datawinners_university()
        overview_page.navigate_to_subjects_page()
        self._verify_datawinners_university()
        overview_page.navigate_to_datasenders_page()
        self._verify_datawinners_university()

    def _verify_datawinners_university(self):
        self.assertTrue(self.dw_university_page.is_help_content_available())
        self.dw_university_page.close_help()

    def _navigate_to_overview_page(self, project_name="clinic test project1"):
        all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        return all_project_page.navigate_to_project_overview_page(project_name)
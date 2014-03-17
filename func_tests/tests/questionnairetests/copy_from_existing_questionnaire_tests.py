import unittest
from framework.base_test import setup_driver, teardown_driver
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.projects.questionnairetests.project_questionnaire_data import COPY_PROJECT_QUESTIONNAIRE_DATA, COPY_PROJECT_DATA


class TestCopyExistingQuestionnaire(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver(browser="phantom")
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        cls.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        cls.project_name, cls.questionnaire_code = cls._create_project(COPY_PROJECT_DATA, COPY_PROJECT_QUESTIONNAIRE_DATA)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def test_to_copy_existing_questionnaire(self):
        create_questionnaire_options_page = self.global_navigation.navigate_to_dashboard_page()\
                                                .navigate_to_create_project_page()
        actual_questions = create_questionnaire_options_page.get_questions_list_for_selected_project(self.project_name)
        self.assertListEqual(["Some dummy question"], actual_questions, "Questions should match existing questions on questionnaire tab")
        create_questionnaire_page = create_questionnaire_options_page.continue_to_questionnaire_page()
        self.assertListEqual(["Some dummy question"], create_questionnaire_page.get_existing_questions())
        self.assertEqual("French", create_questionnaire_page.get_questionnaire_language())
        new_project_title = create_questionnaire_page.set_questionnaire_title("copied project", generate_random=True)
        create_questionnaire_page.save_and_create_project_successfully(click_ok=False)
        self.global_navigation.navigate_to_view_all_project_page().navigate_to_create_project_page()
        self.assertIn(new_project_title, create_questionnaire_options_page.get_project_list())


    @classmethod
    def _create_project(cls, project_data, questionnaire_data):
        global_navigation = GlobalNavigationPage(cls.driver)
        dashboard_page = global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        cls.create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()
        cls.create_questionnaire_page.create_questionnaire_with(project_data, questionnaire_data)
        questionnaire_code = cls.create_questionnaire_page.get_questionnaire_code()
        cls.create_questionnaire_page.set_questionnaire_language("French")
        overview_page = cls.create_questionnaire_page.save_and_create_project_successfully()
        cls.questionnaire_tab_page = overview_page.navigate_to_questionnaire_tab()
        return overview_page.get_project_title(), questionnaire_code


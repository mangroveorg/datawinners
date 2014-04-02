# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from time import sleep
from django.test import Client
from nose.plugins.attrib import attr
from selenium.webdriver.support.wait import WebDriverWait

from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import by_css
from pages.loginpage.login_page import login
from pages.smsquestionnairepreviewpage.sms_questionnaire_preview_page import SmsQuestionnairePreviewPage
from testdata.test_data import *
from tests.projects.overview.project_overview_data import PROJECT_NAME, PREVIEW_TITLE, MC_QUESTION_CONTENT
from tests.testdatasetup.project import create_multi_choice_project
from tests.testsettings import UI_TEST_TIMEOUT


class TestProjectOverview(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.dashboard = login(cls.driver)

    @attr('functional_test')
    def test_project_overview_sms_questionnaire(self):
        all_project_page = self.dashboard.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(PROJECT_NAME)
        light_box = project_overview_page.open_sms_questionnaire_preview()
        self.assertEqual(light_box.get_title_of_light_box(), PREVIEW_TITLE)
        sms_questionnaire_preview_page = SmsQuestionnairePreviewPage(self.driver)
        self.assertTrue(sms_questionnaire_preview_page.has_preview_steps())
        self.assertEqual(MC_QUESTION_CONTENT, sms_questionnaire_preview_page.get_question_content(5))

    @attr('functional_test')
    def test_rename_project_should_reindex_ds(self):
        self.client = Client()
        self.client.login(username='tester150411@gmail.com', password='tester150411')
        project_id = create_multi_choice_project(self.client)
        self.driver.go_to(url('/project/overview/%s' %project_id))
        project_name = self.driver.find(by_css(".project_title")).text
        self.driver.find(by_css(".project_title")).click()
        self.enter_project_name_and_validate_error_msg("clinic test project", "Questionnaire with same name already exists.")
        self.enter_project_name_and_validate_error_msg("", "This field is required.")

        self.driver.find_text_box(by_css(".project_title input.editField")).enter_text("renamed_%s" %project_name)
        self.driver.find(by_css(".project_title .editFieldSaveControllers button")).click()
        WebDriverWait(self.driver._driver, UI_TEST_TIMEOUT).until_not(lambda driver: driver.find_elements_by_css_selector('.editFieldSaveControllers button'))
        self.driver.go_to(url("/project/registered_datasenders/%s/" % project_id))
        self.assertTrue(self.driver.find(by_css(".project_title")).text.startswith("renamed"), self.driver.find(by_css(".project_title")).text)

    def enter_project_name_and_validate_error_msg(self, project_name_text, message):
        self.driver.find_text_box(by_css(".project_title input.editField")).enter_text(project_name_text)
        self.driver.find(by_css(".project_title .editFieldSaveControllers button")).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css(".error .message"))
        WebDriverWait(self.driver._driver, UI_TEST_TIMEOUT).until(lambda driver: driver.find_element_by_css_selector(".error .message").text != "")
        self.assertEqual(self.driver.find(by_css(".error .message")).text, message)
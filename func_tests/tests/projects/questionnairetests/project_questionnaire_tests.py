# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from django.utils.unittest.case import SkipTest

from nose.plugins.attrib import attr
import time

from framework.base_test import setup_driver, teardown_driver
from framework.utils.data_fetcher import fetch_, from_
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import LoginPage
from pages.previewnavigationpage.preview_navigation_page import PreviewNavigationPage
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_SMS_TESTER_PAGE, url
from tests.endtoendtest.end_to_end_data import VALID_DATA_FOR_PROJECT, QUESTIONNAIRE_DATA
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.projects.questionnairetests.project_questionnaire_data import *
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from pages.warningdialog.warning_dialog import WarningDialog
from framework.utils.common_utils import by_id, by_css, random_string


CLOSE_WARNING_DIALOGUE_LINK = by_css(
    'div.ui-dialog[style*="block"] > div.ui-dialog-titlebar>a.ui-dialog-titlebar-close')


def verify_on_edit_project_page(verify_edit_page_functionality):
    project_overview_page = verify_edit_page_functionality()
    return project_overview_page.navigate_to_edit_project_page()


class TestProjectQuestionnaire(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver(browser="phantom")
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        cls.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        global_navigation = GlobalNavigationPage(cls.driver)
        dashboard_page = global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        cls.create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)


    def test_editing_existing_questionnaire(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.create_questionnaire_with(EDIT_PROJECT_DATA, EDIT_PROJECT_QUESTIONNAIRE_DATA)
        overview_page = create_questionnaire_page.save_and_create_project_successfully()
        questionnaire_tab_page = overview_page.navigate_to_questionnaire_tab()
        self.assertIn(EDIT_PROJECT_DATA[PROJECT_NAME], questionnaire_tab_page.get_questionnaire_title())
        self.assertEqual(questionnaire_tab_page.get_existing_questions_count(),
                         len(EDIT_PROJECT_QUESTIONNAIRE_DATA[QUESTIONS]), "Question count does not match")
        expected_existing_questions = [question[QUESTION] for question in EDIT_PROJECT_QUESTIONNAIRE_DATA[QUESTIONS]]
        self.assertEqual(questionnaire_tab_page.get_existing_question_list(), expected_existing_questions,
                         "Mismatch in question list")


    @SkipTest
    def test_successful_questionnaire_editing(self):
        """
        Function to test the successful editing of a Questionnaire with given details
        """
        create_questionnaire_page = self.create_or_navigate_to_project_questionnaire_page()

        new_questionnaire_code = "code" + random_string(3)
        self.verify_questions(create_questionnaire_page)

        def verify_warning_for_deleting_an_option_in_multi_choice_question():
            create_questionnaire_page.select_question_link(5)
            create_questionnaire_page.delete_option_for_multiple_choice_question(2)
            return self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)


        def verify_warning_for_adding_an_option_to_multi_choice_question():
            create_questionnaire_page.select_question_link(5)
            create_questionnaire_page.add_option_to_a_multiple_choice_question("new option")
            return self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)


        def verify_warning_for_numeric_range_modification():
            create_questionnaire_page.select_question_link(2)
            create_questionnaire_page.change_number_question_limit(max_value=30, min_value=5)
            return self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

        def verify_warning_for_word_type_for_character_length_change():
            create_questionnaire_page.select_question_link(1)
            create_questionnaire_page.set_word_question_max_length(25)
            return self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

        def verify_warning_for_date_format_change():
            create_questionnaire_page.select_question_link(3)
            create_questionnaire_page.change_date_type_question(MM_DD_YYYY)
            return self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

        def verify_warning_for_addintion_of_new_question():
            new_question = {"question": "newly added question", "code": "grades", "type": "number",
                            "min": "1", "max": "100"}
            time.sleep(2)
            create_questionnaire_page.add_question(new_question)
            return self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

        def verify_warning_for_change_in_questionnaire_code():
            create_questionnaire_page.set_questionnaire_code(new_questionnaire_code)
            #to get the focus out
            create_questionnaire_page.select_question_link(3)
            return self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

        def verify_warning_for_change_in_question_text():
            create_questionnaire_page.change_question_text(3, "question number 3")
            return self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

        verify_on_edit_project_page(verify_warning_for_adding_an_option_to_multi_choice_question)
        verify_on_edit_project_page(verify_warning_for_deleting_an_option_in_multi_choice_question)
        verify_on_edit_project_page(verify_warning_for_numeric_range_modification)
        verify_on_edit_project_page(verify_warning_for_word_type_for_character_length_change)
        verify_on_edit_project_page(verify_warning_for_date_format_change)
        verify_on_edit_project_page(verify_warning_for_addintion_of_new_question)
        verify_on_edit_project_page(verify_warning_for_change_in_questionnaire_code)
        verify_on_edit_project_page(verify_warning_for_change_in_question_text)

        self.sms_preview_of_questionnaire_on_the_questionnaire_tab(self.project_name)
        self.web_preview_of_questionnaire_on_the_questionnaire_tab()
        self.smart_phone_preview_of_questionnaire_on_the_questionnaire_tab()

        self.verify_sms_submission_after_edit(new_questionnaire_code)

    def verify_questions(self, create_questionnaire_page):
        questions = fetch_(QUESTIONS, from_(QUESTIONNAIRE_DATA_CLINIC_PROJECT))
        #create_questionnaire_page.select_question_link(2)
        #self.driver.find(by_css("#question_title")).click()
        #assert self.driver.find_visible_element(by_id("periode_green_message"))
        #create_questionnaire_page.select_question_link(3)
        #tip_message_element = self.driver.find(by_id('periode_green_message'))
        #self.assertFalse(tip_message_element.is_displayed())
        create_questionnaire_page.select_question_link(1)
        self.assertEqual(questions[0], create_questionnaire_page.get_word_type_question())
        create_questionnaire_page.select_question_link(2)
        self.assertEqual(questions[1], create_questionnaire_page.get_number_type_question())
        create_questionnaire_page.select_question_link(3)
        self.assertEqual(questions[2], create_questionnaire_page.get_date_type_question())
        create_questionnaire_page.select_question_link(4)
        self.assertEqual(questions[3], create_questionnaire_page.get_list_of_choices_type_question())
        create_questionnaire_page.select_question_link(5)
        self.assertEqual(questions[4], create_questionnaire_page.get_list_of_choices_type_question())

    def sms_preview_of_questionnaire_on_the_questionnaire_tab(self, project_name):
        preview_navigation_page = PreviewNavigationPage(self.driver)
        sms_questionnaire_preview_page = preview_navigation_page.sms_questionnaire_preview()

        self.assertIsNotNone(sms_questionnaire_preview_page.sms_questionnaire())
        self.assertEqual(sms_questionnaire_preview_page.get_project_name(), project_name)
        self.assertIsNotNone(sms_questionnaire_preview_page.get_sms_instruction())

        sms_questionnaire_preview_page.close_preview()
        self.assertFalse(sms_questionnaire_preview_page.sms_questionnaire_exist())

    def web_preview_of_questionnaire_on_the_questionnaire_tab(self):
        preview_navigation_page = PreviewNavigationPage(self.driver)
        web_questionnaire_preview_page = preview_navigation_page.web_questionnaire_preview()

        self.assertIsNotNone(web_questionnaire_preview_page.get_web_instruction())
        web_questionnaire_preview_page.close_preview()

    def smart_phone_preview_of_questionnaire_on_the_questionnaire_tab(self):
        preview_navigation_page = PreviewNavigationPage(self.driver)
        smart_phone_preview_page = preview_navigation_page.smart_phone_preview()
        self.assertIsNotNone(smart_phone_preview_page.get_smart_phone_instruction())
        smart_phone_preview_page.close_preview()

    def add_question_to_project(self, create_questionnaire_page):
        question_name = "how many grades did you get last year?"
        new_question = {"question": question_name, "code": "grades", "type": "number",
                        "min": "1", "max": "100"}
        create_questionnaire_page.add_question(new_question)
        create_questionnaire_page.save_and_create_project_successfully()

        return question_name

    def confirm_warning_dialog(self, element_id):
        confirm_locator = by_id(element_id)
        warning_dialog = WarningDialog(self.driver, confirm_link=confirm_locator)
        warning_dialog.confirm()

    def expect_redistribute_dialog_to_be_shown(self, create_questionnaire_page):
        create_questionnaire_page.save_and_create_project(click_ok=False)
        warning_dialog = WarningDialog(self.driver)
        message = warning_dialog.get_message()
        self.assertEqual(message, REDISTRIBUTE_QUESTIONNAIRE_MSG)
        warning_dialog.confirm()
        self.driver.wait_for_page_with_title(20, 'Projects - Overview')
        return ProjectOverviewPage(self.driver)

    def create_or_navigate_to_project_questionnaire_page(self):
        project_overview_page = self.create_new_project()
        return project_overview_page.navigate_to_questionnaire_tab()

    @classmethod
    def create_new_project(cls):
        if cls.project_name:
            all_project_page = cls.global_navigation.navigate_to_view_all_project_page()
            overview_page = all_project_page.navigate_to_project_overview_page(cls.project_name)
            return overview_page

        dashboard_page = cls.global_navigation.navigate_to_dashboard_page()
        questionnaire_creation_options_page = dashboard_page.navigate_to_create_project_page()
        create_questionnaire_page = questionnaire_creation_options_page.select_blank_questionnaire_creation_option()
        create_questionnaire_page = create_questionnaire_page.create_questionnaire_with(CLINIC_PROJECT_DATA,
                                                                                        QUESTIONNAIRE_DATA_CLINIC_PROJECT)

        overview_page = create_questionnaire_page.save_and_create_project_successfully()
        cls.project_name = overview_page.get_project_title()
        return overview_page

    def verify_sms_submission_after_edit(self, new_questionnaire_code):
        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        sms_tester_page = SMSTesterPage(self.driver)
        VALID_SMS[SMS] = new_questionnaire_code + ' mino 25 05.12.2010 a d -18.1324,27.6547 45'
        sms_tester_page.send_sms_with(VALID_SMS)
        message = sms_tester_page.get_response_message()
        self.assertTrue(fetch_(SUCCESS_MESSAGE, VALID_SMS) in message, "message:" + message)


    def goto_dashboard(self):
        self.driver.go_to(url("/dashboard/"))
        return DashboardPage(self.driver)

    @SkipTest
    def test_successful_questionnaire_creation(self):
        questionnaire_creation_options_page = self.goto_dashboard().navigate_to_create_project_page()
        create_questionnaire_page = questionnaire_creation_options_page.select_blank_questionnaire_creation_option()
        create_questionnaire_page.create_questionnaire_with(CLINIC_PROJECT_DATA,
                                                            QUESTIONNAIRE_DATA_WITH_MANY_MC_QUSTIONS)
        index = 1
        for question in fetch_(QUESTIONS, from_(QUESTIONNAIRE_DATA_WITH_MANY_MC_QUSTIONS)):
            question_link_text = fetch_(QUESTION, from_(question))
            self.assertEquals(create_questionnaire_page.get_question_link_text(index), question_link_text)
            index += 1
        overview_page = create_questionnaire_page.save_and_create_project_successfully()
        project_name = overview_page.get_project_title()
        self.assertTrue(fetch_(PROJECT_NAME, from_(CLINIC_PROJECT_DATA)) in project_name)


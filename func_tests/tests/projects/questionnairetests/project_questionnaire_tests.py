# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from django.utils.unittest.case import SkipTest

from nose.plugins.attrib import attr
import time

from framework.base_test import setup_driver, teardown_driver, HeadlessRunnerTest
from framework.utils.data_fetcher import fetch_, from_
from pages.createquestionnairepage.create_questionnaire_page import MANDATORY_FIELD_ERROR_MESSAGE
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import LoginPage
from pages.previewnavigationpage.preview_navigation_page import PreviewNavigationPage
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from pages.projectspage.projects_page import ProjectsPage
from pages.questionnairetabpage.questionnaire_tab_page import SUCCESS_PROJECT_SAVE_MESSAGE, DUPLICATE_QUESTIONNAIRE_CODE_MESSAGE
from pages.warningdialog.questionnaire_modified_dialog import QuestionnaireModifiedDialog
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_SMS_TESTER_PAGE, url, DATA_WINNER_ALL_PROJECTS_PAGE
from tests.endtoendtest.end_to_end_data import VALID_DATA_FOR_PROJECT, QUESTIONNAIRE_DATA
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.projects.questionnairetests.project_questionnaire_data import *
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from pages.warningdialog.warning_dialog import WarningDialog
from framework.utils.common_utils import by_id, by_css, random_string, by_xpath


CLOSE_WARNING_DIALOGUE_LINK = by_css(
    'div.ui-dialog[style*="block"] > div.ui-dialog-titlebar>a.ui-dialog-titlebar-close')


def verify_on_edit_project_page(verify_edit_page_functionality):
    project_overview_page = verify_edit_page_functionality()
    return project_overview_page.navigate_to_edit_project_page()


class TestProjectQuestionnaire(HeadlessRunnerTest):

    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        cls.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        cls.project_name, cls.questionnaire_code = cls._create_project(EDIT_PROJECT_DATA, EDIT_PROJECT_QUESTIONNAIRE_DATA)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @classmethod
    def _create_project(cls, project_data, questionnaire_data):
        global_navigation = GlobalNavigationPage(cls.driver)
        dashboard_page = global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        cls.create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()
        cls.create_questionnaire_page.create_questionnaire_with(project_data, questionnaire_data)
        questionnaire_code = cls.create_questionnaire_page.get_questionnaire_code()
        overview_page = cls.create_questionnaire_page.save_and_create_project_successfully()
        cls.questionnaire_tab_page = overview_page.navigate_to_questionnaire_tab()
        return overview_page.get_project_title(), questionnaire_code

    @attr('functional_test')
    def test_editing_existing_questionnaire(self):
        self.global_navigation.navigate_to_view_all_project_page()
        ProjectsPage(self.driver).navigate_to_project_overview_page(TestProjectQuestionnaire.project_name)\
                                 .navigate_to_questionnaire_tab()
        questionnaire_tab_page = self.questionnaire_tab_page
        self.assertEqual(questionnaire_tab_page.get_select_or_edit_question_message(),
                         "Select a question to edit or add another question.",
                         "No question should be selected by default")
        self.assertIn(EDIT_PROJECT_DATA[PROJECT_NAME], questionnaire_tab_page.get_questionnaire_title())
        self.assertEqual(questionnaire_tab_page.get_existing_questions_count(),
                         len(EDIT_PROJECT_QUESTIONNAIRE_DATA[QUESTIONS]), "Question count does not match")
        expected_existing_questions = [question[QUESTION] for question in EDIT_PROJECT_QUESTIONNAIRE_DATA[QUESTIONS]]
        self.assertEqual(questionnaire_tab_page.get_existing_question_list(), expected_existing_questions,
                         "Mismatch in question list")
        questionnaire_tab_page.submit_questionnaire()
        self.assertEqual(questionnaire_tab_page.get_success_message(), SUCCESS_PROJECT_SAVE_MESSAGE, "Saving of unaltered questionnaire failed")

    @attr('functional_test')
    def test_add_question_with_invalid_selections(self):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.refresh()
        self._validate_word_answer_type()
        self._validate_number_answer_type()
        self._validate_multiple_choice_type()
        self._validate_unique_id_type()


    @attr('functional_test')
    def test_adding_questions_with_valid_answer_types(self):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.refresh()
        project_title, questionnaire_code = self._create_project(QUESTIONNAIRE_TAB_PROJECT_DATA, QUESTIONNAIRE_TAB_QUESTIONNAIRE_DATA)
        self.do_sms_submission(questionnaire_code, QUESTIONNAIRE_TAB_SUBMISSION_SMS, project_title)
        questionnaire_tab_page.select_question_link(1)
        questionnaire_tab_page.change_answer_type_to_choice_question()
        self.assertEqual("default", questionnaire_tab_page.get_nth_option_choice_text(1), "Default text should be present for 1st choice") #Bug - 3152
        questionnaire_tab_page.delete_question(1)
        self._expect_delete_question_dialog_to_be_shown(proceed=False)
        self.assertEqual(questionnaire_tab_page.get_existing_questions_count(), 1, "Question should not be deleted.")
        questionnaire_tab_page.delete_question(1)
        self._expect_delete_question_dialog_to_be_shown(proceed=True)
        questionnaire_tab_page.submit_questionnaire()
        self._expect_empty_questionnaire_dialog_to_be_shown()
        questionnaire_tab_page.add_questions(ADDITIONAL_TAB_QUESTIONNAIRE_DATA)
        questionnaire_tab_page.set_questionnaire_code(TestProjectQuestionnaire.questionnaire_code)
        questionnaire_tab_page.submit_questionnaire()
        self.assertEqual(questionnaire_tab_page.get_error_message(), DUPLICATE_QUESTIONNAIRE_CODE_MESSAGE, "Duplicate error message not shown")
        questionnaire_tab_page.set_questionnaire_code(questionnaire_code)
        questionnaire_tab_page.submit_questionnaire()
        self.assertEqual(questionnaire_tab_page.get_success_message(), SUCCESS_PROJECT_SAVE_MESSAGE, "Saving of questionnaire failed")
        self._expect_redistribute_dialog_to_be_shown()
        self.assertEqual(questionnaire_tab_page.get_existing_questions_count(), 8, "Question count of updated questionnaire does not match")

    @attr('functional_test')
    def test_should_show_warning_popup_when_exiting_a_modified_questionnaire(self):
        modified_warning_dialog = QuestionnaireModifiedDialog(self.driver)
        self._verify_edit_dialog_cancel(modified_warning_dialog)
        self._verify_edit_dialog_ignore_changes(modified_warning_dialog)
        self._verify_edit_dialog_save_changes(modified_warning_dialog)

    def _verify_edit_dialog_cancel(self, modified_warning_dialog):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.click_add_question_link()
        questionnaire_tab_page.set_question_title("some question")
        questionnaire_tab_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[0])
        questionnaire_tab_page.submit_questionnaire()
        self.global_navigation.navigate_to_dashboard_page()
        self.assertTrue(modified_warning_dialog.is_visible(), "Should show modified warning dialog");
        modified_warning_dialog.cancel()
        self.assertEqual(questionnaire_tab_page.get_questionnaire_title(), self.project_name,
                         "Should continue to stay on questionnaire page")

    def _verify_edit_dialog_ignore_changes(self, modified_warning_dialog):
        questionnaire_tab_page = self.questionnaire_tab_page
        all_projects_page = self.global_navigation.navigate_to_view_all_project_page()
        self.assertTrue(modified_warning_dialog.is_visible(), "Should show modified warning dialog")
        modified_warning_dialog.ignore_changes()
        all_projects_page.navigate_to_project_overview_page(self.project_name).navigate_to_questionnaire_tab()
        self.assertNotIn("some question", questionnaire_tab_page.get_existing_question_list(), "Newly added question should not have been saved")

    def _verify_edit_dialog_save_changes(self, modified_warning_dialog):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.click_add_question_link()
        questionnaire_tab_page.set_question_title("some question")
        questionnaire_tab_page.change_question_type(WATERPOINT_QUESTIONNAIRE_DATA[QUESTIONS][0])
        all_projects_page = self.global_navigation.navigate_to_view_all_project_page()
        self.assertTrue(modified_warning_dialog.is_visible(), "Should show modified warning dialog");
        modified_warning_dialog.save_changes()
        self._expect_redistribute_dialog_to_be_shown()
        all_projects_page.wait_for_page_to_load()
        all_projects_page.navigate_to_project_overview_page(self.project_name).navigate_to_questionnaire_tab()
        self.assertIn("some question", questionnaire_tab_page.get_existing_question_list(), "Newly added question should be saved")

    def do_sms_submission(self, questionnaire_code, sms_data, project_title):
        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        sms_tester_page = SMSTesterPage(self.driver)
        sms_data[SMS] = sms_data[SMS] % questionnaire_code
        sms_tester_page.send_sms_with(sms_data)
        message = sms_tester_page.get_response_message()
        self.assertTrue(fetch_(SUCCESS_MESSAGE, sms_data) in message, "message:" + message)
        self.driver.go_to(DATA_WINNER_ALL_PROJECTS_PAGE)
        ProjectsPage(self.driver).navigate_to_project_overview_page(project_title)\
                                 .navigate_to_questionnaire_tab()


    def _validate_multiple_choice_type(self):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.click_add_question_link()
        questionnaire_tab_page.set_question_title("Choice question")
        questionnaire_tab_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[3])
        questionnaire_tab_page.click_add_question_link()
        self._validate_errored_choice_inputs()
        self._validate_valid_choice_inputs()
        #cleaning up state
        questionnaire_tab_page.delete_question(10)
        questionnaire_tab_page.delete_question(9)

    def _validate_valid_choice_inputs(self):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.change_nth_option_of_choice(1, "choice1")
        questionnaire_tab_page.change_nth_option_of_choice(2, "choice2")
        questionnaire_tab_page.change_nth_option_of_choice(3, "choice3")
        questionnaire_tab_page.click_add_question_link()
        self.assertEqual(questionnaire_tab_page.get_existing_questions_count(), 10,
                         "Choice question should not have validation errors")

    def _validate_errored_choice_inputs(self):
        questionnaire_tab_page = self.questionnaire_tab_page
        is_visible, message = questionnaire_tab_page.get_choice_error_message(index=1)
        self.assertTrue(is_visible, "Choice1 error message message not displayed")
        self.assertEqual(message, MANDATORY_FIELD_ERROR_MESSAGE, "Error message is incorrect for choice1")
        is_visible, message = questionnaire_tab_page.get_choice_error_message(index=2)
        self.assertTrue(is_visible, "Choice2 error message message not displayed")
        self.assertEqual(message, MANDATORY_FIELD_ERROR_MESSAGE, "Error message is incorrect for choice2")
        is_visible, message = questionnaire_tab_page.get_choice_error_message(index=3)
        self.assertTrue(is_visible, "Choice3 error message message not displayed")
        self.assertEqual(message, MANDATORY_FIELD_ERROR_MESSAGE, "Error message is incorrect for choice3")
        questionnaire_tab_page.delete_option_for_multiple_choice_question(3)
        questionnaire_tab_page.delete_option_for_multiple_choice_question(2)
        questionnaire_tab_page.add_choice_option_to_selected_question()
        is_visible, message = questionnaire_tab_page.get_choice_error_message(index=2)
        self.assertFalse(is_visible, "Newly added question should not have error message")
        questionnaire_tab_page.add_choice_option_to_selected_question()
        is_visible, message = questionnaire_tab_page.get_choice_error_message(index=3)
        self.assertFalse(is_visible, "Newly added question should not have error message")

    def _validate_number_answer_type(self):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.click_add_question_link()
        questionnaire_tab_page.set_question_title("Some title")
        self._validate_range_with_non_number_input()
        self._validate_range_for_max_less_than_min_input()
        self._validate_range_for_valid_input()
        #cleaning up state
        questionnaire_tab_page.delete_question(10)
        questionnaire_tab_page.delete_question(9)

    def _validate_range_for_valid_input(self):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.set_min_range_limit(5)
        questionnaire_tab_page.click_add_question_link()
        is_visible, message = questionnaire_tab_page.get_min_range_error_message()
        self.assertFalse(is_visible, "Min range error message should not displayed for valid input")
        is_visible, message = questionnaire_tab_page.get_max_range_error_message()
        self.assertFalse(is_visible, "Max range error message should not displayed for valid input")


    def _validate_range_for_max_less_than_min_input(self):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.change_number_question_limit(max_value=10, min_value=100)
        questionnaire_tab_page.click_add_question_link()
        is_visible, message = questionnaire_tab_page.get_max_range_error_message()
        self.assertTrue(is_visible, "Max range error message not displayed")
        self.assertEqual(message, "Max should be greater than min.", "Error message is incorrect")
        is_visible, message = questionnaire_tab_page.get_min_range_error_message()
        self.assertFalse(is_visible, "Min range error message should not displayed for valid input")


    def _validate_range_with_non_number_input(self):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[1])
        questionnaire_tab_page.click_add_question_link()
        is_visible, message = questionnaire_tab_page.get_min_range_error_message()
        self.assertTrue(is_visible, "Min range error message not displayed")
        self.assertEqual(message, "Please insert a valid number.", "Error message is incorrect")
        is_visible, message = questionnaire_tab_page.get_max_range_error_message()
        self.assertTrue(is_visible, "Max range error message not displayed")
        self.assertEqual(message, "Please insert a valid number.", "Error message is incorrect")

    def _validate_word_answer_type(self):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.click_add_question_link()
        questionnaire_tab_page.set_question_title("Some title")
        self._validate_max_length_for_invalid_entry()
        self._validate_max_length_for_mandatory_entry()
        self._validate_max_length_for_valid_entry()
        #cleaning up state
        questionnaire_tab_page.delete_question(10)
        questionnaire_tab_page.delete_question(9)

    def _validate_max_length_for_invalid_entry(self):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[0])
        questionnaire_tab_page.click_add_question_link()
        is_visible, message = questionnaire_tab_page.get_max_length_error_message()
        self.assertTrue(is_visible, "Max length error message not displayed")
        self.assertEqual(message, "Please insert a valid number.", "Error message is incorrect")

    def _validate_max_length_for_mandatory_entry(self):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.set_word_question_max_length("")
        questionnaire_tab_page.click_add_question_link()
        is_visible, message = questionnaire_tab_page.get_max_length_error_message()
        self.assertTrue(is_visible, "Max length error message not displayed")
        self.assertEqual(message, "This field is required.", "Error message is incorrect")

    def _validate_max_length_for_valid_entry(self):
        questionnaire_tab_page = self.questionnaire_tab_page
        questionnaire_tab_page.set_word_question_max_length(10)
        questionnaire_tab_page.click_add_question_link()
        is_visible, message = questionnaire_tab_page.get_max_length_error_message()
        self.assertFalse(is_visible, "Max length error message should not be displayed for valid length")


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
            return self._expect_redistribute_dialog_to_be_shown(create_questionnaire_page)


        def verify_warning_for_adding_an_option_to_multi_choice_question():
            create_questionnaire_page.select_question_link(5)
            create_questionnaire_page.add_option_to_a_multiple_choice_question("new option")
            return self._expect_redistribute_dialog_to_be_shown(create_questionnaire_page)


        def verify_warning_for_numeric_range_modification():
            create_questionnaire_page.select_question_link(2)
            create_questionnaire_page.change_number_question_limit(max_value=30, min_value=5)
            return self._expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

        def verify_warning_for_word_type_for_character_length_change():
            create_questionnaire_page.select_question_link(1)
            create_questionnaire_page.set_word_question_max_length(25)
            return self._expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

        def verify_warning_for_date_format_change():
            create_questionnaire_page.select_question_link(3)
            create_questionnaire_page.change_date_type_question(MM_DD_YYYY)
            return self._expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

        def verify_warning_for_addintion_of_new_question():
            new_question = {"question": "newly added question", "code": "grades", "type": "number",
                            "min": "1", "max": "100"}
            time.sleep(2)
            create_questionnaire_page.add_question(new_question)
            return self._expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

        def verify_warning_for_change_in_questionnaire_code():
            create_questionnaire_page.set_questionnaire_code(new_questionnaire_code)
            #to get the focus out
            create_questionnaire_page.select_question_link(3)
            return self._expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

        def verify_warning_for_change_in_question_text():
            create_questionnaire_page.change_question_text(3, "question number 3")
            return self._expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

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

    def _expect_redistribute_dialog_to_be_shown(self):
        warning_dialog = WarningDialog(self.driver)
        message = warning_dialog.get_message()
        self.assertEqual(message, REDISTRIBUTE_QUESTIONNAIRE_MSG)
        warning_dialog.confirm()

    def _expect_delete_question_dialog_to_be_shown(self, proceed=False):
        warning_dialog = WarningDialog(self.driver)
        message = warning_dialog.get_message()
        self.assertEqual(message, DELETE_QUESTION_MSG)
        if proceed:
            warning_dialog.confirm()
        else:
            warning_dialog.cancel()

    def _expect_empty_questionnaire_dialog_to_be_shown(self):
        warning_dialog = WarningDialog(self.driver, confirm_link=by_xpath(".//*[@id='no_questions_exists']/div/a"))
        message = warning_dialog.get_message()
        self.assertEqual(message, EMPTY_QUESTIONNAIRE_MSG)
        warning_dialog.confirm()

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

    def _validate_unique_id_type(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.set_question_title("Unique Id question")
        create_questionnaire_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[6])
        create_questionnaire_page.click_add_question_link()
        self._validate_errored_unique_id_input(create_questionnaire_page)

        create_questionnaire_page.delete_question(9)
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.set_question_title("Unique Id question")
        create_questionnaire_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[7])
        self._validate_duplicate_unique_id(create_questionnaire_page)
        #cleaning up state
        create_questionnaire_page.delete_question(9)


    def _validate_errored_unique_id_input(self, create_questionnaire_page):
        is_visible, message = create_questionnaire_page.get_unique_id_error_msg()
        self.assertTrue(is_visible, "Mandatory validaton error msg for unique id not visible")
        self.assertEqual(message, MANDATORY_FIELD_ERROR_MESSAGE, "Error message is incorrect for choice1")

    def _validate_duplicate_unique_id(self, create_questionnaire_page):
        new_type_name = fetch_(NEW_UNIQUE_ID_TYPE, from_(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[7]))

        create_questionnaire_page.add_new_unique_id_type(new_type_name)
        is_visible, message = create_questionnaire_page.get_new_unique_id_error_msg()
        self.assertTrue(is_visible)
        self.assertEqual(message, '%s already registered as a subject type.' % new_type_name)

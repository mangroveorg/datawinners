from nose.plugins.attrib import attr
from framework.base_test import teardown_driver, HeadlessRunnerTest
from framework.utils.data_fetcher import fetch_, from_
from pages.loginpage.login_page import login
from pages.projectspage.projects_page import ProjectsPage
from pages.questionnairetabpage.questionnaire_tab_page import MANDATORY_FIELD_ERROR_MESSAGE
from pages.warningdialog.questionnaire_modified_dialog import QuestionnaireModifiedDialog
from tests.projects.questionnairetests.project_questionnaire_data import QUESTIONS_WITH_INVALID_ANSWER_DETAILS, WATERPOINT_QUESTIONNAIRE_DATA, QUESTIONS, DIALOG_PROJECT_DATA, NEW_UNIQUE_ID_TYPE
from django.utils.unittest.case import SkipTest

@SkipTest #Lastly, These tests were not ran, cause of __init__ file missing.
class TestCreateBlankQuestionnaire(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation = login(cls.driver)
        dashboard_page = cls.global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        cls.create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()


    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @attr('functional_test')
    def test_should_not_select_any_question_by_default(self):
        self.create_questionnaire_page.refresh()
        select_or_add_question_message = self.create_questionnaire_page.get_select_or_edit_question_message()
        self.assertTrue(select_or_add_question_message.is_displayed(), "Select/add question text not present")

    @attr('functional_test')
    def test_should_clear_questionnaire_form_on_recreating_questionnaire(self):
        create_questionnaire_page = self.create_questionnaire_page
        self.create_questionnaire_page.refresh()
        create_questionnaire_page.set_questionnaire_title("Some title")
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.change_question_type(WATERPOINT_QUESTIONNAIRE_DATA[QUESTIONS][0])
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[0])
        create_questionnaire_page.submit_errored_questionnaire()
        create_questionnaire_page.back_to_questionnaire_creation_page().select_blank_questionnaire_creation_option()
        self.assertEqual(create_questionnaire_page.get_questionnaire_title(), "", "Questionnaire title should be blank")
        self.assertEqual(create_questionnaire_page.get_existing_questions_count(), 0,
                         "No questions should be present for a blank questionnaire")
        self.assertTrue(create_questionnaire_page.get_select_or_edit_question_message().is_displayed(),
                        "No question should be selected by default")

    @attr('functional_test')
    def test_submitting_a_blank_questionnaire(self):
        self.global_navigation.navigate_to_view_all_project_page().navigate_to_create_project_page() \
            .select_blank_questionnaire_creation_option()
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.set_questionnaire_title("")
        create_questionnaire_page.set_questionnaire_code("")
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.submit_errored_questionnaire()
        is_visible, message = create_questionnaire_page.get_questionnaire_title_error_message()
        self.assertTrue(is_visible, "Questionnaire title error message not displayed")
        self.assertEqual(message, MANDATORY_FIELD_ERROR_MESSAGE, "Error message is incorrect")
        is_visible, message = create_questionnaire_page.get_questionnaire_code_error_message()
        self.assertTrue(is_visible, "Questionnaire code error message not displayed")
        self.assertEqual(message, MANDATORY_FIELD_ERROR_MESSAGE, "Error message is incorrect")
        create_questionnaire_page.set_questionnaire_title("Functional test - Errored project")
        create_questionnaire_page.set_questionnaire_code("proj23")
        create_questionnaire_page.delete_question(1)
        self.assertFalse(create_questionnaire_page.is_empty_submission_popup_present(),
                         "Empty Questionnaire popup should come up only on submitting")
        create_questionnaire_page.submit_errored_questionnaire()
        self.assertTrue(create_questionnaire_page.is_empty_submission_popup_present(),
                        "Empty Questionnaire popup did not show up")

    @attr('functional_test')
    def test_add_question_with_invalid_selections(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.refresh()
        self._validate_word_answer_type()
        self._validate_number_answer_type()
        self._validate_multiple_choice_type()
        self._validate_unique_id_type()

    @attr('functional_test')
    def test_submitting_a_questionnaire_with_already_existing_questionnaire_code(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.refresh()
        create_questionnaire_page.set_questionnaire_title("Duplicate project")
        create_questionnaire_page.set_questionnaire_code("cli051")
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.set_question_title("Some qn")
        create_questionnaire_page.change_question_type(WATERPOINT_QUESTIONNAIRE_DATA[QUESTIONS][0])
        create_questionnaire_page.submit_errored_questionnaire()
        self.assertEqual(create_questionnaire_page.get_duplicate_questionnaire_code_error_message(),
                         "Questionnaire with this code already exists", "Duplicate questionnaire code should show up")

    @attr('functional_test')
    def test_should_show_warning_popup_when_exiting_a_modified_questionnaire(self):
        create_questionnaire_page = self.create_questionnaire_page
        modified_warning_dialog = QuestionnaireModifiedDialog(self.driver)
        project_name = create_questionnaire_page.type_project_name(DIALOG_PROJECT_DATA)
        self._verify_edit_dialog_cancel(modified_warning_dialog)
        self._verify_edit_dialog_ignore_changes(modified_warning_dialog, project_name)
        all_projects_page = ProjectsPage(self.driver)
        self._verify_edit_dialog_save_changes(all_projects_page, modified_warning_dialog)

    def _verify_edit_dialog_cancel(self, modified_warning_dialog):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.set_question_title("some question")
        create_questionnaire_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[0])
        create_questionnaire_page.submit_errored_questionnaire()
        self.global_navigation.navigate_to_dashboard_page()
        self.assertTrue(modified_warning_dialog.is_visible(), "Should show modified warning dialog");
        modified_warning_dialog.cancel()
        self.assertEqual(create_questionnaire_page.get_page_title(), "Create a New Questionnaire",
                         "Should continue to stay on questionnaire page")

    def _verify_edit_dialog_ignore_changes(self, modified_warning_dialog, project_name):
        all_projects_page = self.global_navigation.navigate_to_view_all_project_page()
        self.assertTrue(modified_warning_dialog.is_visible(), "Should show modified warning dialog")
        modified_warning_dialog.ignore_changes()
        self.assertFalse(all_projects_page.is_project_present(project_name), "Project should not have been saved")

    def _verify_edit_dialog_save_changes(self, all_projects_page, modified_warning_dialog):
        create_questionnaire_page = self.create_questionnaire_page
        all_projects_page.navigate_to_create_project_page().select_blank_questionnaire_creation_option()
        project_name = create_questionnaire_page.type_project_name(DIALOG_PROJECT_DATA)
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.set_question_title("some question")
        create_questionnaire_page.change_question_type(WATERPOINT_QUESTIONNAIRE_DATA[QUESTIONS][0])
        all_projects_page = self.global_navigation.navigate_to_view_all_project_page()
        self.assertTrue(modified_warning_dialog.is_visible(), "Should show modified warning dialog");
        modified_warning_dialog.save_changes()
        all_projects_page.wait_for_page_to_load()
        self.assertTrue(all_projects_page.is_project_present(project_name.lower()), "Project should be saved")

    def _validate_max_length_for_invalid_entry(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[0])
        create_questionnaire_page.click_add_question_link()
        is_visible, message = create_questionnaire_page.get_max_length_error_message()
        self.assertTrue(is_visible, "Max length error message not displayed")
        self.assertEqual(message, "Please insert a valid number.", "Error message is incorrect")

    def _validate_max_length_for_mandatory_entry(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.set_word_question_max_length("")
        create_questionnaire_page.click_add_question_link()
        is_visible, message = create_questionnaire_page.get_max_length_error_message()
        self.assertTrue(is_visible, "Max length error message not displayed")
        self.assertEqual(message, "This field is required.", "Error message is incorrect")


    def _validate_max_length_for_valid_entry(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.set_word_question_max_length(10)
        create_questionnaire_page.click_add_question_link()
        is_visible, message = create_questionnaire_page.get_max_length_error_message()
        self.assertFalse(is_visible, "Max length error message should not be displayed for valid length")

    def _validate_word_answer_type(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.set_question_title("Some title")
        self._validate_max_length_for_invalid_entry()
        self._validate_max_length_for_mandatory_entry()
        self._validate_max_length_for_valid_entry()
        #cleaning up state
        create_questionnaire_page.delete_question(2)
        create_questionnaire_page.delete_question(1)


    def _validate_range_with_non_number_input(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[1])
        create_questionnaire_page.click_add_question_link()
        is_visible, message = create_questionnaire_page.get_min_range_error_message()
        self.assertTrue(is_visible, "Min range error message not displayed")
        self.assertEqual(message, "Please insert a valid number.", "Error message is incorrect")
        is_visible, message = create_questionnaire_page.get_max_range_error_message()
        self.assertTrue(is_visible, "Max range error message not displayed")
        self.assertEqual(message, "Please insert a valid number.", "Error message is incorrect")

    def _validate_range_for_max_less_than_min_input(self):
        create_questionnaire_page = self.create_questionnaire_page
        self.create_questionnaire_page.change_number_question_limit(max_value=10, min_value=100)
        create_questionnaire_page.click_add_question_link()
        is_visible, message = create_questionnaire_page.get_max_range_error_message()
        self.assertTrue(is_visible, "Max range error message not displayed")
        self.assertEqual(message, "Max should be greater than min.", "Error message is incorrect")
        is_visible, message = create_questionnaire_page.get_min_range_error_message()
        self.assertFalse(is_visible, "Min range error message should not displayed for valid input")

    def _validate_range_for_valid_input(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.set_min_range_limit(5)
        create_questionnaire_page.click_add_question_link()
        is_visible, message = create_questionnaire_page.get_min_range_error_message()
        self.assertFalse(is_visible, "Min range error message should not displayed for valid input")
        is_visible, message = create_questionnaire_page.get_max_range_error_message()
        self.assertFalse(is_visible, "Max range error message should not displayed for valid input")

    def _validate_number_answer_type(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.set_question_title("Some title")
        self._validate_range_with_non_number_input()
        self._validate_range_for_max_less_than_min_input()
        self._validate_range_for_valid_input()
        #cleaning up state
        create_questionnaire_page.delete_question(2)
        create_questionnaire_page.delete_question(1)

    def _validate_errored_choice_inputs(self, create_questionnaire_page):
        is_visible, message = create_questionnaire_page.get_choice_error_message(index=1)
        self.assertTrue(is_visible, "Choice1 error message message not displayed")
        self.assertEqual(message, MANDATORY_FIELD_ERROR_MESSAGE, "Error message is incorrect for choice1")
        is_visible, message = create_questionnaire_page.get_choice_error_message(index=2)
        self.assertTrue(is_visible, "Choice2 error message message not displayed")
        self.assertEqual(message, MANDATORY_FIELD_ERROR_MESSAGE, "Error message is incorrect for choice2")
        is_visible, message = create_questionnaire_page.get_choice_error_message(index=3)
        self.assertTrue(is_visible, "Choice3 error message message not displayed")
        self.assertEqual(message, MANDATORY_FIELD_ERROR_MESSAGE, "Error message is incorrect for choice3")
        create_questionnaire_page.delete_option_for_multiple_choice_question(3)
        create_questionnaire_page.delete_option_for_multiple_choice_question(2)
        create_questionnaire_page.add_choice_option_to_selected_question()
        is_visible, message = create_questionnaire_page.get_choice_error_message(index=2)
        self.assertFalse(is_visible, "Newly added question should not have error message")
        create_questionnaire_page.add_choice_option_to_selected_question()
        is_visible, message = create_questionnaire_page.get_choice_error_message(index=3)
        self.assertFalse(is_visible, "Newly added question should not have error message")

    def _validate_valid_choice_inputs(self, create_questionnaire_page):
        create_questionnaire_page.change_nth_option_of_choice(1, "choice1")
        create_questionnaire_page.change_nth_option_of_choice(2, "choice2")
        create_questionnaire_page.change_nth_option_of_choice(3, "choice3")
        create_questionnaire_page.click_add_question_link()
        self.assertEqual(create_questionnaire_page.get_existing_questions_count(), 2,
                         "Choice question should not have validation errors")

    def _validate_multiple_choice_type(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.set_question_title("Choice question")
        create_questionnaire_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[3])
        create_questionnaire_page.click_add_question_link()
        self._validate_errored_choice_inputs(create_questionnaire_page)
        self._validate_valid_choice_inputs(create_questionnaire_page)
        #cleaning up state
        create_questionnaire_page.delete_question(2)
        create_questionnaire_page.delete_question(1)

    def _validate_unique_id_type(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.set_question_title("Unique Id question")
        create_questionnaire_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[6])
        create_questionnaire_page.click_add_question_link()
        self._validate_errored_unique_id_input(create_questionnaire_page)

        create_questionnaire_page.delete_question(1)
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.set_question_title("Unique Id question")
        create_questionnaire_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[7])
        self._validate_duplicate_unique_id(create_questionnaire_page)
        #cleaning up state
        create_questionnaire_page.delete_question(1)


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

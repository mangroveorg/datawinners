import unittest
from framework.base_test import setup_driver, teardown_driver
from pages.createquestionnairepage.create_questionnaire_page import MANDATORY_FIELD_ERROR_MESSAGE
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.projects.questionnairetests.project_questionnaire_data import QUESTIONS_WITH_INVALID_ANSWER_DETAILS


class TestCreateBlankQuestionnaire(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_name = None
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

    def test_should_not_select_any_question_by_default(self):
        self.create_questionnaire_page.refresh()
        select_or_add_question_message = self.create_questionnaire_page.get_select_or_edit_question_message()
        self.assertTrue(select_or_add_question_message.is_displayed(), "Select/add question text not present")

    def test_submitting_a_blank_questionnaire(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.refresh()
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
        create_questionnaire_page.submit_errored_questionnaire()
        self.assertTrue(create_questionnaire_page.is_empty_submission_popup_present(),
                        "Empty Questionnaire popup did not show up")

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


    def test_add_question_with_invalid_selections(self):
        create_questionnaire_page = self.create_questionnaire_page
        create_questionnaire_page.refresh()
        self._validate_word_answer_type()
        self._validate_number_answer_type()
        self._validate_multiple_choice_type()

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






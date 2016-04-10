from nose.plugins.attrib import attr

from framework.utils.data_fetcher import fetch_, from_
from framework.base_test import HeadlessRunnerTest, setup_driver
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import login
from tests.websubmissiontests.web_submission_data import *
from tests.logintests.login_data import VALID_CREDENTIALS


class TestWebSubmission(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver("firefox")
        login(cls.driver, VALID_CREDENTIALS)

    dashboard_page = None

    def submit_web_submission(self):
        web_submission_page = self.navigate_to_web_submission()
        self.driver.wait_for_page_with_title(5,web_submission_page.get_title())
        web_submission_page.fill_questionnaire_with(VALID_ANSWERS)
        web_submission_page.submit_answers()
        return web_submission_page

    def navigate_to_web_submission(self, questionaire=None):
        all_data_page = (GlobalNavigationPage(self.driver)).navigate_to_all_data_page()
        if questionaire is not None :
            return all_data_page.navigate_to_web_submission_page(
                fetch_(PROJECT_NAME, from_(questionaire)))
        else:
            return all_data_page.navigate_to_web_submission_page(
                fetch_(PROJECT_NAME, from_(DEFAULT_ORG_DATA)))

    def fill_repeat_autocomplete_test(self,web_submission_page):
        repeat_number = fetch_(SECTION_REPEAT_NUMBER, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA))
        print repeat_number
        cpt = 1
        while cpt <= repeat_number:
            web_submission_page.fill_select_with_autocomplete_appearance_in_repeat(
                repeat_name = fetch_(SECTION_REPEAT_NAME, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)),
                repeat_number = cpt,
                field_name = fetch_(FIELD_SELECT1_IDNR_AUTOCOMPLETE_IN_REPEAT_NAME, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)),
                value = fetch_(FIELD_SELECT1_IDNR_AUTOCOMPLETE_IN_REPEAT_INPUT_VALUE, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA))
            )
            idnr_autocomplete_in_repeat_suggestions = web_submission_page.get_select_with_autocomplete_appearance_suggestions()
            self.assertEqual(idnr_autocomplete_in_repeat_suggestions,
                             fetch_(FIELD_SELECT1_IDNR_AUTOCOMPLETE_IN_REPEAT_ASSERT, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA))
                             )
            web_submission_page.select_select_with_autocomplete_appearance_suggestion(
                fetch_(FIELD_SELECT1_IDNR_AUTOCOMPLETE_IN_REPEAT_VALUE, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA))
            )
            web_submission_page.fill_input_field_in_repeat(fetch_(SECTION_REPEAT_NAME, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)),
                                                 cpt,
                                                 fetch_(FIELD_INPUT_IN_REPEAT_NAME, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)),
                                                 fetch_(FIELD_INPUT_IN_REPEAT_VALUE, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA))
                                                 )

            if repeat_number >= (cpt+1):
                web_submission_page.add_section_repeat(fetch_(SECTION_REPEAT_NAME, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)),cpt)
                cpt += 1
            else:
                return None
            # import time
            # time.sleep(2)

    @attr('functional_test')
    def test_successful_web_submission_by_paid_account(self):
        web_submission_page = self.submit_web_submission()
        self.assertEqual(web_submission_page.get_errors(),[])
        self.assertEqual(web_submission_page.get_text_value('NA'), u'')

    @attr('functional_test')
    def test_paid_account_can_do_submission_after_submission_limit(self):
        web_submission_page = self.submit_web_submission()
        self.assertEqual(web_submission_page.get_errors(),[])

    @attr('functional_test')
    def test_should_check_each_questions_has_instruction(self):
        web_submission_page = self.navigate_to_web_submission()
        self.driver.wait_for_page_with_title(5, web_submission_page.get_title())
        questions, instructions = web_submission_page.get_questions_and_instructions()
        self.assertEqual(questions[2], u"What is age \xf6f father?")
        self.assertEqual(instructions[2], "Answer must be a number between 18-100.")

    @attr('functional_test')
    def test_check_select_autocomplete_question(self):
        web_submission_page = self.navigate_to_web_submission(QUESTIONNAIRE_AUTOCOMPLETE_DATA)
        #self.driver.create_screenshot("anaranle_fichier")
        # questions = web_submission_page.fill_questions_in_autocomplete_questionnaire()
        web_submission_page.set_questionnaire_form_id(fetch_(QUESTIONNAIRE_FORM_ID, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)))
        web_submission_page.wait_for_questionnaire_form_loading()
        web_submission_page.fill_input_field(fetch_(FIELD_INPUT_NAME, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)),
                                             fetch_(FIELD_INPUT_VALUE, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)))
        web_submission_page.fill_select_without_appearance(fetch_(FIELD_SELECT1_NAME, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)),
                                                     fetch_(FIELD_SELECT1_VALUE, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)))
        web_submission_page.fill_select_with_minimal_appearance(fetch_(FIELD_SELECT1_MINIMAL_NAME, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)),
                                                     fetch_(FIELD_SELECT1_MINIMAL_NUMBER, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)))
        # autocomplete fed by choices sheet
        web_submission_page.fill_select_with_autocomplete_appearance(fetch_(FIELD_SELECT1_AUTOCOMPLETE_NAME, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)),
                                                     fetch_(FIELD_SELECT1_AUTOCOMPLETE_INPUT_VALUE, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)))
        choices_autocomplete_suggestions = web_submission_page.get_select_with_autocomplete_appearance_suggestions()
        # assertion
        self.assertEqual(choices_autocomplete_suggestions,fetch_(
            FIELD_SELECT1_AUTOCOMPLETE_ASSERT, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA))
                         )
        web_submission_page.select_select_with_autocomplete_appearance_suggestion(
            fetch_(FIELD_SELECT1_AUTOCOMPLETE_VALUE, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA))
        )

        # autocomplete fed by ID Number
        web_submission_page.fill_select_with_autocomplete_appearance(
            fetch_(FIELD_SELECT1_IDNR_AUTOCOMPLETE_NAME, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA)),
            fetch_(FIELD_SELECT1_IDNR_AUTOCOMPLETE_INPUT_VALUE, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA))
        )
        idnr_autocomplete_suggestions = web_submission_page.get_select_with_autocomplete_appearance_suggestions()
        self.assertEqual(idnr_autocomplete_suggestions,
                         fetch_(FIELD_SELECT1_IDNR_AUTOCOMPLETE_ASSERT, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA))
                         )
        web_submission_page.select_select_with_autocomplete_appearance_suggestion(
            fetch_(FIELD_SELECT1_IDNR_AUTOCOMPLETE_VALUE, from_(QUESTIONNAIRE_AUTOCOMPLETE_DATA))
        )
        self.fill_repeat_autocomplete_test(web_submission_page = web_submission_page)
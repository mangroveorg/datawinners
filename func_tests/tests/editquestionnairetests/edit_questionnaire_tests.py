# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.loginpage.login_page import LoginPage
from pages.previewnavigationpage.preview_navigation_page import PreviewNavigationPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_SMS_TESTER_PAGE
from tests.createprojecttests.create_project_data import CREATE_NEW_PROJECT_DATA
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.editquestionnairetests.edit_questionnaire_data import *
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from pages.warningdialog.warning_dialog_page import WarningDialog
from framework.utils.common_utils import  by_id
from nose.plugins.skip import SkipTest
import time

@attr('suit_2')
class TestEditQuestionnaire(BaseTest):
    def setUp(self):
        super(TestEditQuestionnaire, self).setUp()
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        time.sleep(1)
        self.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

    def tearDown(self):
        super(TestEditQuestionnaire, self).tearDown()

    def prerequisites_of_edit_questionnaire(self):
        all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(VALID_PROJECT_DATA)))
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        edit_project_page.continue_create_project()
        return CreateQuestionnairePage(self.driver)

    def prerequisites_of_questionnaire_tab(self):
        all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page("Clinic test project")
        return project_overview_page.navigate_to_questionnaire_tab()

    def test_should_add_questions_to_new_questionnaire(self):
        create_questionnaire_page, project_name = self.create_new_project()
        question_name = self.add_question_to_project(create_questionnaire_page)
        self.go_to_questionnaire_page(project_name)

        self.assertEqual(question_name, create_questionnaire_page.get_last_question_link_text())

    @attr('functional_test', 'smoke')
    def test_successful_questionnaire_editing(self):
        """
        Function to test the successful editing of a Questionnaire with given details
        """
        create_questionnaire_page = self.prerequisites_of_edit_questionnaire()
        questions = fetch_(QUESTIONS, from_(QUESTIONNAIRE_DATA))
        create_questionnaire_page.select_question_link(2)
        self.assertEqual(questions[0], create_questionnaire_page.get_word_type_question())
        create_questionnaire_page.select_question_link(3)
        self.assertEqual(questions[1], create_questionnaire_page.get_number_type_question())
        create_questionnaire_page.select_question_link(4)
        self.assertEqual(questions[2], create_questionnaire_page.get_date_type_question())
        create_questionnaire_page.select_question_link(5)
        self.assertEqual(questions[3], create_questionnaire_page.get_list_of_choices_type_question())
        create_questionnaire_page.select_question_link(6)
        self.assertEqual(questions[4], create_questionnaire_page.get_list_of_choices_type_question())
        first_tab = self.driver.current_window_handle
        create_questionnaire_page.delete_question(7)
        time.sleep(2)
        self.driver.execute_script("window.open('%s')" % DATA_WINNER_SMS_TESTER_PAGE)
        new_tab = self.driver.window_handles[1]
        self.driver.switch_to_window(new_tab)
        sms_tester_page = SMSTesterPage(self.driver)
        sms_tester_page.send_sms_with(VALID_SMS)
        time.sleep(5)
        self.assertEqual(sms_tester_page.get_response_message(), fetch_(SUCCESS_MESSAGE, VALID_SMS))
        self.assertEqual(first_tab, self.driver.window_handles[0])
        self.driver.switch_to_window(first_tab)
        create_questionnaire_page.save_and_create_project()
        time.sleep(4)
        warning_dialog = WarningDialog(self.driver)
        self.assertEqual(SAVE_QUESTIONNAIRE_WITH_NEWLY_COLLECTED_DATA_WARNING, warning_dialog.get_message())
        warning_dialog.cancel()
        create_questionnaire_page.delete_question(5)
        time.sleep(2)
        self.assertEqual(DELETE_QUESTIONNAIRE_WITH_COLLECTED_DATA_WARNING, warning_dialog.get_message())
        warning_dialog.cancel()

    @attr('functional_test')
    def test_sms_preview_of_questionnaire_on_the_questionnaire_tab(self):
        self.prerequisites_of_questionnaire_tab()
        preview_navigation_page = PreviewNavigationPage(self.driver)
        sms_questionnaire_preview_page = preview_navigation_page.sms_questionnaire_preview()

        self.assertIsNotNone(sms_questionnaire_preview_page.sms_questionnaire())
        self.assertEqual(sms_questionnaire_preview_page.get_project_name(), "clinic test project")
        self.assertIsNotNone(sms_questionnaire_preview_page.get_sms_instruction())

        sms_questionnaire_preview_page.close_preview()
        self.assertFalse(sms_questionnaire_preview_page.sms_questionnaire_exist())


    @attr('functional_test')
    def test_web_preview_of_questionnaire_on_the_questionnaire_tab(self):
        self.prerequisites_of_questionnaire_tab()
        preview_navigation_page = PreviewNavigationPage(self.driver)
        web_questionnaire_preview_page = preview_navigation_page.web_questionnaire_preview()

        self.assertIsNotNone(web_questionnaire_preview_page.get_web_instruction())

    @attr('functional_test')
    def test_smart_phone_preview_of_questionnaire_on_the_questionnaire_tab(self):
        self.prerequisites_of_questionnaire_tab()
        preview_navigation_page = PreviewNavigationPage(self.driver)
        smart_phone_preview_page = preview_navigation_page.smart_phone_preview()

        self.assertIsNotNone(smart_phone_preview_page.get_smart_phone_instruction())

    @attr('functional_test')
    def test_should_hide_tip_for_period_question_when_adding_new_question(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)

        # going on all project page
        all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page("clinic6 test project")
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        edit_project_page.continue_create_project()
        create_questionnaire_page = CreateQuestionnairePage(self.driver)
        self.assertFalse(create_questionnaire_page.period_question_tip_is_displayed())
        create_questionnaire_page.change_question_text(4, "new question label")
        time.sleep(1)
        self.assertTrue(create_questionnaire_page.period_question_tip_is_displayed())
        create_questionnaire_page.click_add_question_link()
        self.assertFalse(create_questionnaire_page.period_question_tip_is_displayed())

    @attr('functional_test')
    def test_should_show_warning_when_deleting_question_in_questionnaire_having_data(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        all_subject_page = self.global_navigation.navigate_to_all_subject_page()
        all_subject_page.add_new_subject_type(SUBJECT_TYPE)
        time.sleep(2)
        edit_registration_form = all_subject_page.navigate_to_edit_registration_form(SUBJECT_TYPE, True)
        first_tab = self.driver.current_window_handle
        edit_registration_form.delete_question(5)
        self.driver.execute_script("window.open('%s')" % DATA_WINNER_SMS_TESTER_PAGE)
        new_tab = self.driver.window_handles[1]
        self.driver.switch_to_window(new_tab)
        sms_tester_page = SMSTesterPage(self.driver)
        sms_tester_page.send_sms_with(VALID_SMS_SUBJECT_DATA)
        time.sleep(1)
        self.assertEqual(sms_tester_page.get_response_message(), fetch_(SUCCESS_MESSAGE, VALID_SMS_SUBJECT_DATA))
        self.assertEqual(first_tab, self.driver.window_handles[0])
        self.driver.close()
        self.driver.switch_to_window(first_tab)
        warning_dialog = WarningDialog(self.driver)
        edit_registration_form.save_questionnaire()
        self.assertEqual(SAVE_QUESTIONNAIRE_WITH_NEWLY_COLLECTED_DATA_WARNING, warning_dialog.get_message())
        warning_dialog.cancel()
        edit_registration_form.delete_question(4)
        self.assertEqual(DELETE_QUESTIONNAIRE_WITH_COLLECTED_DATA_WARNING, warning_dialog.get_message())

    def create_new_project(self):
        dashboard_page = self.global_navigation.navigate_to_dashboard_page()
        create_project_page = dashboard_page.navigate_to_create_project_page()
        create_project_page.create_project_with(CREATE_NEW_PROJECT_DATA)
        project_name = create_project_page.get_project_name()
        create_project_page.continue_create_project()
        create_questionnaire_page = CreateQuestionnairePage(self.driver)

        return create_questionnaire_page, project_name

    def add_question_to_project(self, create_questionnaire_page):
        question_name = "how many grades did you get last year?"
        new_question = {"question": question_name, "code": "grades", "type": "number",
                        "min": "1", "max": "100"}
        create_questionnaire_page.add_question(new_question)
        create_questionnaire_page.save_and_create_project_successfully()

        return question_name

    def go_to_questionnaire_page(self, project_name):
        all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(project_name)
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        edit_project_page.continue_create_project()

    def cancle_warning_dialog(self, element_id="option_warning_message_cancel"):
        cancel_locator = by_id(element_id)
        warning_dialog = WarningDialog(self.driver, cancel_link=cancel_locator)
        warning_dialog.cancel()

    def confirm_warning_dialog(self, element_id):
        confirm_locator = by_id(element_id)
        warning_dialog = WarningDialog(self.driver, confirm_link=confirm_locator)
        warning_dialog.confirm()


    def create_project_and_add_one_question(self, question_type="word"):
        time.sleep(2)
        create_questionnaire_page, project_name = self.create_new_project()
        number_question = {"question": "number", "code": "grades", "type": "number",
                        "min": "1", "max": "100"}
        word_question = {"question": "word", "code": "word", "type": "word",
                        "limit": "10"}
        multiple_choice_question = {"question": "MC question", "code": "mc", "type": "list_of_choices",
                        "allowed_choice": "only_one_answer", "choice": ["first", "second", "third"]}
        date_question = {"question": "Date question", "code": "d", "type": "date",
                        "date_format": "mm.yyyy"}

        questions = {"word": word_question,
                     "number": number_question,
                     "choice": multiple_choice_question,
                     "date": date_question}
        question = questions.get(question_type, None)
        if question: create_questionnaire_page.add_question(question)

        return create_questionnaire_page, project_name

    @attr('functional_test')
    def test_should_show_redistribute_questionnaire_message_when_osi_delete_an_mc_question_option(self):
        create_questionnaire_page = self.prerequisites_for_redistribute_questionnaire_dialog("choice")
        create_questionnaire_page.select_question_link(3)
        create_questionnaire_page.delete_option_for_multiple_choice_question(2)
        self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

    @SkipTest
    @attr('functional_test')
    def test_should_show_redistribute_questionnaire_message_when_osi_change_an_mc_question_option(self):
        create_questionnaire_page = self.prerequisites_for_redistribute_questionnaire_dialog("choice")
        create_questionnaire_page.select_question_link(3)
        create_questionnaire_page.change_nth_option_of_choice(2, "changed value")
        #to get the focus out
        create_questionnaire_page.select_question_link(3)
        self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

    @attr('functional_test')
    def test_should_show_redistribute_questionnaire_message_when_osi_delete_a_question(self):
        create_questionnaire_page = self.prerequisites_for_redistribute_questionnaire_dialog()
        create_questionnaire_page.delete_question(3)
        time.sleep(4)
        self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

    @attr('functional_test')
    def test_should_show_redistribute_questionnaire_message_when_osi_change_limit_for_numeric_question(self):
        create_questionnaire_page = self.prerequisites_for_redistribute_questionnaire_dialog("number")
        create_questionnaire_page.select_question_link(3)
        create_questionnaire_page.change_number_question_limit(30, min_value=5)
        self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

    @attr('functional_test')
    def test_should_show_redistribute_questionnaire_message_when_osi_change_limit_for_word_question(self):
        create_questionnaire_page = self.prerequisites_for_redistribute_questionnaire_dialog()
        create_questionnaire_page.select_question_link(3)
        create_questionnaire_page.set_word_question_max_length(25)
        self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

    @attr('functional_test')
    def test_should_show_redistribute_questionnaire_message_when_osi_change_date_format_for_date_question(self):
        create_questionnaire_page = self.prerequisites_for_redistribute_questionnaire_dialog("date")
        create_questionnaire_page.select_question_link(3)
        create_questionnaire_page.change_date_type_question("dd.mm.yyyy")
        self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

    @attr('functional_test')
    def test_should_show_redistribute_questionnaire_message_when_osi_add_a_new_question(self):
        create_questionnaire_page = self.prerequisites_for_redistribute_questionnaire_dialog()
        new_question = {"question": "newly added question", "code": "grades", "type": "number",
                        "min": "1", "max": "100"}
        create_questionnaire_page.add_question(new_question)
        self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

    @attr('functional_test')
    def test_should_show_redistribute_questionnaire_message_when_osi_change_questionnaire_code(self):
        create_questionnaire_page = self.prerequisites_for_redistribute_questionnaire_dialog()
        create_questionnaire_page.set_questionnaire_code("nfc")
        #to get the focus out
        create_questionnaire_page.select_question_link(3)
        self.confirm_warning_dialog(element_id="ok_button")
        self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

    @attr('functional_test')
    def test_should_show_redistribute_questionnaire_message_when_osi_change_question_title(self):
        create_questionnaire_page = self.prerequisites_for_redistribute_questionnaire_dialog()
        create_questionnaire_page.change_question_text(3, "question number 3")
        self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

    @attr('functional_test')
    def test_should_show_redistribute_questionnaire_message_when_osi_add_an_mc_question_option(self):
        create_questionnaire_page = self.prerequisites_for_redistribute_questionnaire_dialog("choice")
        create_questionnaire_page.select_question_link(3)
        create_questionnaire_page.add_option_to_a_multiple_choice_question("new option")
        self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

    @attr('functional_test')
    def test_should_show_redistribute_questionnaire_message_when_osi_change_answer_type_for_mc_question_option(self):
        create_questionnaire_page = self.prerequisites_for_redistribute_questionnaire_dialog("choice")
        create_questionnaire_page.select_question_link(3)
        create_questionnaire_page.change_list_of_choice_answer_type("multiple_answers")
        self.expect_redistribute_dialog_to_be_shown(create_questionnaire_page)

    def prerequisites_for_redistribute_questionnaire_dialog(self, question_type="word"):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        time.sleep(1)
        create_questionnaire_page, project_name = self.create_project_and_add_one_question(question_type)
        project_overview = create_questionnaire_page.save_and_create_project_successfully()
        self.assertEqual(project_overview.get_project_title(), project_name)
        edit_project_page = project_overview.navigate_to_edit_project_page()
        edit_project_page.continue_create_project()
        return create_questionnaire_page

    def expect_redistribute_dialog_to_be_shown(self, create_questionnaire_page):
        create_questionnaire_page.save_and_create_project(click_ok=False)
        warning_dialog = WarningDialog(self.driver)
        message = warning_dialog.get_message()
        self.assertEqual(message, REDISTRIBUTE_QUESTIONNAIRE_MSG)
        warning_dialog.confirm()
        #title = self.driver.get_title()
        #self.driver.wait_for_page_with_title(10000, "Projects - Overview")
        #self.assertEqual(title, "Projects - Overview")
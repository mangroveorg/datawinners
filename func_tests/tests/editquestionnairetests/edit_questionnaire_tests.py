# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.lightbox.light_box_page import LightBox
from pages.loginpage.login_page import LoginPage
from pages.previewnavigationpage.preview_navigation_page import PreviewNavigationPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_SMS_TESTER_PAGE
from tests.createprojecttests.create_project_data import CREATE_NEW_PROJECT_DATA
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.editquestionnairetests.edit_questionnaire_data import *
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from pages.warningdialog.warning_dialog_page import WarningDialog
from framework.utils.common_utils import  by_id
import time

@attr('suit_2')
class TestEditQuestionnaire(BaseTest):
    def setUp(self):
        super(TestEditQuestionnaire, self).setUp()
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        self.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

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
        self.assertEqual(sms_tester_page.get_response_message(), fetch_(SUCCESS_MESSAGE, VALID_SMS))
        self.assertEqual(first_tab, self.driver.window_handles[0])
        self.driver.switch_to_window(first_tab)
        create_questionnaire_page.save_and_create_project()
        time.sleep(2)
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
    def test_change_date_format_of_report_period_should_show_warning_message_and_clear_submissions(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)

        # going on all project page
        all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page("clinic6 test project")
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        edit_project_page.continue_create_project()
        create_questionnaire_page = CreateQuestionnairePage(self.driver)
        create_questionnaire_page.select_question_link(4)
        create_questionnaire_page.change_date_type_question(MM_YYYY)
        light_box = LightBox(self.driver)
        self.assertEquals(light_box.get_title_of_light_box(), fetch_(TITLE, from_(LIGHT_BOX_DATA)))
        self.assertEquals(light_box.get_message_from_light_box(), fetch_(MESSAGE, from_(LIGHT_BOX_DATA)))
        light_box.continue_change_date_format()
        project_overview_page = create_questionnaire_page.save_and_create_project_successfully()
        data_analysis_page = project_overview_page.navigate_to_data_page()
        self.assertEqual(1, len(data_analysis_page.get_all_data_records()))

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

    @attr("functional_test")
    def test_should_warn_when_changing_answer_type(self):
        create_questionnaire_page = self.prerequisites_of_edit_questionnaire()
        create_questionnaire_page.change_question_type_to(2, "date")
        warning_dialog = WarningDialog(self.driver)
        message = warning_dialog.get_message()
        self.assertEqual(message, CHANGE_QUESTION_TYPE_MSG)

    @attr("functional_test")
    def test_should_get_the_type_back_when_canceling_the_type_change(self):
        create_questionnaire_page = self.prerequisites_of_edit_questionnaire()
        create_questionnaire_page.change_question_type_to(2, "date")
        self.cancle_warning_dialog()
        type = create_questionnaire_page.get_question_type(2)
        self.assertEqual(type, "text")

    @attr("functional_test")
    def test_should_get_the_type_back_when_canceling_the_change_of_single_choice_type(self):
        create_questionnaire_page = self.prerequisites_of_edit_questionnaire()
        create_questionnaire_page.change_question_type_to(5, "date")
        self.cancle_warning_dialog()
        type = create_questionnaire_page.get_question_type(5)
        self.assertEqual(type, "choice")

    @attr("functional_test")
    def test_should_get_the_type_back_when_canceling_the_change_of_multiple_choice_type(self):
        create_questionnaire_page = self.prerequisites_of_edit_questionnaire()
        create_questionnaire_page.change_question_type_to(6, "date")
        self.cancle_warning_dialog()
        type = create_questionnaire_page.get_question_type(6)
        self.assertEqual(type, "choice")

    @attr("functional_test")
    def test_should_change_the_question_type_when_confirming_the_type_change(self):
        create_questionnaire_page = self.prerequisites_of_edit_questionnaire()
        create_questionnaire_page.change_question_type_to(2, "date")
        confirm_locator = by_id("option_warning_message_continue")
        warning_dialog = WarningDialog(self.driver, confirm_link=confirm_locator)
        warning_dialog.confirm()
        type = create_questionnaire_page.get_question_type(2)
        self.assertEqual(type, "date")

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

    def cancle_warning_dialog(self):
        cancel_locator = by_id("option_warning_message_cancel")
        warning_dialog = WarningDialog(self.driver, cancel_link=cancel_locator)
        warning_dialog.cancel()

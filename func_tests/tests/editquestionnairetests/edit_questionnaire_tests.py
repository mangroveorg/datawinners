# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.lightbox.light_box_page import LightBox
from pages.loginpage.login_page import LoginPage
from pages.previewnavigationpage.preview_navigation_page import PreviewNavigationPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_SMS_TESTER_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.editquestionnairetests.edit_questionnaire_data import *
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from pages.warningdialog.warning_dialog_page import WarningDialog
import time

@attr('suit_2')
class TestEditQuestionnaire(BaseTest):
    def prerequisites_of_edit_questionnaire(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(VALID_PROJECT_DATA)))
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        edit_project_page.continue_create_project()
        return CreateQuestionnairePage(self.driver)

    def prerequisites_of_questionnaire_tab(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page("Clinic test project")
        return project_overview_page.navigate_to_questionnaire_tab()

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
        self.driver.execute_script("window.open('%s')" % DATA_WINNER_SMS_TESTER_PAGE)
        new_tab = self.driver.window_handles[1]
        self.driver.switch_to_window(new_tab)
        sms_tester_page = SMSTesterPage(self.driver)
        sms_tester_page.send_sms_with(VALID_SMS)
        self.assertEqual(sms_tester_page.get_response_message(), fetch_(SUCCESS_MESSAGE, VALID_SMS))
        self.assertEqual(first_tab, self.driver.window_handles[0])
        self.driver.switch_to_window(first_tab)
        warning_dialog = WarningDialog(self.driver)
        create_questionnaire_page.save_and_create_project()
        time.sleep(2)
        self.assertEqual(SAVE_QUESTIONNAIRE_WITH_NEWLY_COLLECTED_DATA_WARNING, warning_dialog.get_message())
        warning_dialog.cancel()
        create_questionnaire_page.delete_question(5)
        time.sleep(2)
        self.assertEqual(DELETE_QUESTIONNAIRE_WITH_COLLECTED_DATA_WARNING, warning_dialog.get_message())

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
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        all_project_page = global_navigation.navigate_to_view_all_project_page()
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
        project_overview_page = create_questionnaire_page.save_and_create_project_successfully( )
        data_analysis_page = project_overview_page.navigate_to_data_page( )
        self.assertEqual(1, len(data_analysis_page.get_all_data_records()))

    @attr('functional_test')
    def test_should_hide_tip_for_period_question_when_adding_new_question(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        all_project_page = global_navigation.navigate_to_view_all_project_page()
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
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all subject page
        all_subject_page = global_navigation.navigate_to_all_subject_page()
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
        

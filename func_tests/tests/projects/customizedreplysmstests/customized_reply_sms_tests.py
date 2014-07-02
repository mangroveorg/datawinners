from nose.plugins.attrib import attr

from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import random_string
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.languagespage.customized_language_locator import SUCCESS_SUBMISSION_MESSAGE_LOCATOR, SUBMISSION_WITH_ERROR_MESSAGE_LOCATOR, SUBMISSION_WITH_INCORRECT_NUMBER_OF_RESPONSES_LOCATOR, RESPONSE_ERROR_MESSAGE_FROM_UNAUTHORIZED_SOURCE_LOCATOR, SUBMISSION_WITH_INCORRECT_UNIQUE_ID
from pages.loginpage.login_page import login
from pages.projectspage.projects_page import ProjectsPage
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from testdata.test_data import DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_ALL_PROJECTS_PAGE
from tests.projects.customizedreplysmstests.customized_reply_sms_data import PROJECT_DATA, PROJECT_QUESTIONNAIRE_DATA, get_success_sms_data_with_questionnaire_code, get_error_message_from_unauthorized_source, get_error_sms_data_with_incorrect_number_of_answers, get_error_sms_data_with_questionnaire_code, get_error_sms_data_with_incorrect_unique_id


class TestCustomizedReplySms(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation = login(cls.driver)
        cls.automatic_reply_sms_page = cls._create_project_and_go_to_automatic_reply_sms_page(PROJECT_DATA, PROJECT_QUESTIONNAIRE_DATA)

    @classmethod
    def _create_project_and_go_to_automatic_reply_sms_page(cls, project_data, questionnaire_data):
        global_navigation = GlobalNavigationPage(cls.driver)
        dashboard_page = global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        cls.create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()
        cls.create_questionnaire_page.create_questionnaire_with(project_data, questionnaire_data)
        questionnaire_code = cls.create_questionnaire_page.get_questionnaire_code()
        overview_page = cls.create_questionnaire_page.save_and_create_project_successfully()
        cls.project_name = overview_page.get_project_title()
        cls.questionnaire_code = questionnaire_code
        broadcast_message_page = overview_page.navigate_send_message_tab()
        return broadcast_message_page.navigate_to_automatic_reply_sms_page()

    def change_project_language(self, new_language, project_name):
        global_navigation = GlobalNavigationPage(self.driver)
        all_projects_page = global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_projects_page.navigate_to_project_overview_page(project_name)
        broadcast_message_page = project_overview_page.navigate_send_message_tab()
        automatic_reply_sms_page = broadcast_message_page.navigate_to_automatic_reply_sms_page()
        automatic_reply_sms_page.choose_automatic_reply_language(new_language)
        automatic_reply_sms_page.save_changes()
        self.assertEqual(automatic_reply_sms_page.get_success_message(), 'Your changes have been saved.')

    @attr('functional_test')
    def test_project_reply_sms_language(self):
        languages_page = self.automatic_reply_sms_page.choose_automatic_reply_language('new')
        new_language = 'kannada' + random_string(4)
        languages_page.add_new_language(new_language)
        self.assertEqual(languages_page.get_success_message(), 'Your language has been added successfully. Please translate the suggested automatic reply SMS text.')
        languages_page.wait_till_success_message_box_disappears()

        languages_page.append_custom_message_for(SUCCESS_SUBMISSION_MESSAGE_LOCATOR, 'Dhanyawaadagalu')

        languages_page.append_custom_message_for(SUBMISSION_WITH_ERROR_MESSAGE_LOCATOR, 'Tappu uttara')
        languages_page.append_custom_message_for(SUBMISSION_WITH_INCORRECT_NUMBER_OF_RESPONSES_LOCATOR, 'Tappada sankhyeya uttaragalu')
        languages_page.append_custom_message_for(SUBMISSION_WITH_INCORRECT_UNIQUE_ID, 'daakhaleyalli illa')
        languages_page.append_custom_message_for(RESPONSE_ERROR_MESSAGE_FROM_UNAUTHORIZED_SOURCE_LOCATOR, 'Nimage anumathi illa')

        languages_page.save_changes()
        self.assertEqual(languages_page.get_success_message(), 'Changes saved successfully.')

        self.change_project_language(new_language, self.project_name)

        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        sms_tester_page = SMSTesterPage(self.driver)

        sms_data = get_success_sms_data_with_questionnaire_code(self.questionnaire_code)
        sms_tester_page.send_sms_with(sms_data)
        message = sms_tester_page.get_response_message()
        self.assertIn('Dhanyawaadagalu', message)

        sms_data = get_error_sms_data_with_questionnaire_code(self.questionnaire_code)
        sms_tester_page.send_sms_with(sms_data)
        self.assertIn('Tappu uttara', sms_tester_page.get_response_message())

        sms_data = get_error_sms_data_with_incorrect_number_of_answers(self.questionnaire_code)
        sms_tester_page.send_sms_with(sms_data)
        self.assertIn('Tappada sankhyeya uttaragalu' , sms_tester_page.get_response_message())

        sms_data = get_error_sms_data_with_incorrect_unique_id(self.questionnaire_code)
        sms_tester_page.send_sms_with(sms_data)
        self.assertIn('daakhaleyalli illa', sms_tester_page.get_response_message())

        sms_data = get_error_message_from_unauthorized_source(self.questionnaire_code)
        sms_tester_page.send_sms_with(sms_data)
        self.assertIn('Nimage anumathi illa', sms_tester_page.get_response_message())

    @attr('functional_test')
    def test_reply_messages_in_light_box_when_outgoing_reply_turned_off(self):
        self.driver.go_to(DATA_WINNER_ALL_PROJECTS_PAGE)
        automatic_reply_msg_page = ProjectsPage(self.driver).navigate_to_project_overview_page(self.project_name).navigate_send_message_tab().navigate_to_automatic_reply_sms_page()
        automatic_reply_msg_page.turn_off_reply_messages()
        self.assertFalse(automatic_reply_msg_page.is_language_selection_enabled())
        self.assertEqual(automatic_reply_msg_page.get_success_message(), 'Your changes have been saved.')

        sms_tester_light_box = automatic_reply_msg_page.open_sms_tester_light_box()

        self.assertTrue(sms_tester_light_box.reply_turned_off_text_present())

        sms_tester_light_box.send_sms_with(get_success_sms_data_with_questionnaire_code(self.questionnaire_code))
        self.assertEquals("", sms_tester_light_box.get_response_message())

        sms_tester_light_box.send_sms_with(get_error_sms_data_with_questionnaire_code(self.questionnaire_code))
        self.assertEquals("", sms_tester_light_box.get_response_message())

        sms_tester_light_box.send_sms_with(get_error_sms_data_with_incorrect_number_of_answers(self.questionnaire_code))
        self.assertEquals("", sms_tester_light_box.get_response_message())

        sms_tester_light_box.send_sms_with(get_error_sms_data_with_incorrect_unique_id(self.questionnaire_code))
        self.assertEquals("", sms_tester_light_box.get_response_message())

        sms_tester_light_box.send_sms_with(get_error_message_from_unauthorized_source(self.questionnaire_code))
        self.assertEquals("", sms_tester_light_box.get_response_message())

        #account wide messages should still go out.

        sms_tester_light_box.send_sms_with(get_success_sms_data_with_questionnaire_code('invalid_code'))
        self.assertNotEqual("", sms_tester_light_box.get_response_message())

        success_subject_registration_data = {"from": "1234123413", "to": '919880734937', "sms": "peo fname lname location 4,4 898989898" }
        sms_tester_light_box.send_sms_with(success_subject_registration_data)
        self.assertNotEqual("", sms_tester_light_box.get_response_message())

        success_subject_registration_data_with_existing_code = {"from": "1234123413", "to": '919880734937', "sms": "peo fname lname location 4,4 898989898 cid001" }
        sms_tester_light_box.send_sms_with(success_subject_registration_data_with_existing_code)
        self.assertNotEqual("", sms_tester_light_box.get_response_message())


    @attr('functional_test')
    def test_reply_messages_in_light_box_when_outgoing_reply_turned_on(self):
        self.driver.go_to(DATA_WINNER_ALL_PROJECTS_PAGE)
        automatic_reply_msg_page = ProjectsPage(self.driver).navigate_to_project_overview_page(self.project_name).navigate_send_message_tab().navigate_to_automatic_reply_sms_page()
        automatic_reply_msg_page.turn_on_reply_messages()
        self.assertTrue(automatic_reply_msg_page.is_language_selection_enabled())
        self.assertEqual(automatic_reply_msg_page.get_success_message(), 'Your changes have been saved.')

        sms_tester_light_box = automatic_reply_msg_page.open_sms_tester_light_box()

        self.assertFalse(sms_tester_light_box.reply_turned_off_text_present())

        sms_tester_light_box.send_sms_with(get_success_sms_data_with_questionnaire_code(self.questionnaire_code))
        self.assertNotEquals("", sms_tester_light_box.get_response_message())

        sms_tester_light_box.send_sms_with(get_error_sms_data_with_questionnaire_code(self.questionnaire_code))
        self.assertNotEquals("", sms_tester_light_box.get_response_message())

        sms_tester_light_box.send_sms_with(get_error_sms_data_with_incorrect_number_of_answers(self.questionnaire_code))
        self.assertNotEquals("", sms_tester_light_box.get_response_message())

        sms_tester_light_box.send_sms_with(get_error_sms_data_with_incorrect_unique_id(self.questionnaire_code))
        self.assertNotEquals("", sms_tester_light_box.get_response_message())

        sms_tester_light_box.send_sms_with(get_error_message_from_unauthorized_source(self.questionnaire_code))
        self.assertNotEquals("", sms_tester_light_box.get_response_message())



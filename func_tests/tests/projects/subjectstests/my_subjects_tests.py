from nose.plugins.attrib import attr
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from framework.base_test import teardown_driver, HeadlessRunnerTest
from pages.loginpage.login_page import login
from tests.projects.subjectstests.my_subjects_data import *


class TestMySubjects(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation = login(cls.driver)

    def setUp(self):
        self.all_project_page = self.global_navigation.navigate_to_view_all_project_page()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @classmethod
    def goto_my_subjects_page(cls, all_project_page, project_name=CLINIC_PROJECT1_NAME):
        project_overview_page = all_project_page.navigate_to_project_overview_page(project_name)
        return project_overview_page.navigate_to_subjects_page()

    @attr("functional_test")
    def test_should_load_actions_dynamically(self):
        self.my_subjects_page = self.goto_my_subjects_page(self.all_project_page)
        self.my_subjects_page.navigate_to_my_subjects_list_tab()
        self.my_subjects_page.wait_for_subject_table_to_load()
        self.my_subjects_page.click_action_button()
        self.assert_none_selected_shown()

        self.my_subjects_page.select_subject_by_row(2)
        self.my_subjects_page.click_action_button()
        self.assert_action_menu_shown_for()

        self.my_subjects_page.select_subject_by_row(3)
        self.my_subjects_page.click_action_button()
        self.assertFalse(self.my_subjects_page.is_edit_disabled())

    def assert_none_selected_shown(self):
        self.assertTrue(self.my_subjects_page.is_none_selected_shown())

    def assert_action_menu_shown_for(self):
        self.assertFalse(self.my_subjects_page.is_edit_disabled())
        self.assertFalse(self.my_subjects_page.is_delete_disabled())
        self.assertFalse(self.my_subjects_page.is_none_selected_shown())

    @attr("functional_test")
    def test_should_uncheck_checkall_if_one_cb_is_unchecked(self):
        self.my_subjects_page = self.goto_my_subjects_page(self.all_project_page)
        self.my_subjects_page.navigate_to_my_subjects_list_tab()
        self.my_subjects_page.wait_for_subject_table_to_load()
        self.my_subjects_page.click_checkall_checkbox()
        self.assertTrue(self.my_subjects_page.is_checkall_checked())
        self.my_subjects_page.select_subject_by_row(2)
        self.assertFalse(self.my_subjects_page.is_checkall_checked())
        self.my_subjects_page.select_subject_by_row(2)
        self.assertTrue(self.my_subjects_page.is_checkall_checked())

    def create_project_with_multiple_unique_ids(self, project_details, questionnaire_details):
        create_questionnaire_options_page = self.all_project_page.navigate_to_create_project_page()
        create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()
        create_questionnaire_page.create_questionnaire_with(project_details, questionnaire_details)
        return create_questionnaire_page.save_and_create_project_successfully()

    @attr("functional_test")
    def test_should_have_multiple_subject_tabs_if_project_has_multiple_unique_id_questions(self):
        project_overview_page = self.create_project_with_multiple_unique_ids(PROJECT_DETAILS,
                                                                             QUESTIONNAIRE_DATA_WITH_MULTIPLE_SUBJECTS)

        self.assertEqual(project_overview_page.subject_tab_text(), "My Identification Numbers")

        identification_number_page = project_overview_page.navigate_to_subjects_page()
        subject_types = identification_number_page.get_subject_type_names()

        for subject_type in subject_types:
            self.assertTrue('Gaming' or 'School' in subject_type)

        active_subject_type = identification_number_page.get_active_subject_type()
        self.assertEqual('Gaming', active_subject_type.split(' ')[0])

        identification_number_page.navigate_to_subject_registration_form_tab()

        active_subject_type = identification_number_page.get_active_subject_type()
        self.assertEqual('Gaming', active_subject_type.split(' ')[0])

        identification_number_page.click_edit_form_link_and_continue()

        active_subject_type = identification_number_page.get_active_subject_type()
        self.assertEqual('Gaming', active_subject_type.split(' ')[0])

        identification_number_page.navigate_to_nth_entity_type(1)

        active_subject_type = identification_number_page.get_active_subject_type()
        self.assertEqual('School', active_subject_type.split(' ')[0])

    @attr("functional_test")
    def test_should_not_display_entity_types_if_only_one_unique_id_question_in_questionnaire(self):
        project_overview_page = self.create_project_with_multiple_unique_ids(PROJECT_DETAILS,
                                                                             QUESTIONNAIRE_DATA_WITH_ONE_SUBJECT)

        self.assertIn("Firestation", project_overview_page.subject_tab_text().split(' '))

        identification_number_page = project_overview_page.navigate_to_subjects_page()
        subject_types = identification_number_page.get_subject_type_names()
        self.assertFalse(subject_types)


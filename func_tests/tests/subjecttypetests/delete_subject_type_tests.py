# vim: ai ts=4 sts=4 et sw=4utf-8
from nose.plugins.attrib import attr

from framework.base_test import teardown_driver, HeadlessRunnerTest
from framework.utils.data_fetcher import from_, fetch_
from framework.utils.common_utils import generateId, random_string
from pages.addsubjecttypepage.add_subject_type_page import AddSubjectTypePage
from pages.loginpage.login_page import login
from testdata.test_data import DATA_WINNER_ALL_SUBJECT
from tests.addsubjecttests.add_subject_data import SUBJECT_DATA_WITHOUT_UNIQUE_ID
from tests.subjecttypetests.add_subject_type_data import *


class TestDeleteSubjectType(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        login(cls.driver)
        cls.driver.go_to(DATA_WINNER_ALL_SUBJECT)
        cls.page = AddSubjectTypePage(cls.driver)

    def setUp(self):
        self.driver.refresh()

    @attr('functional_test')
    def test_should_shown_action_button(self):
        subject_type_page = self.page
        subject_type_page.click_all_subject_type()
        subject_type_page.click_action_button()
        self.assertTrue(subject_type_page.actions_menu_shown())

    @attr('functional_test')
    def test_should_not_shown_action_button(self):
        subject_type_page = self.page
        subject_type_page.click_all_subject_type(check=False)
        subject_type_page.click_action_button()
        self.assertFalse(subject_type_page.actions_menu_shown())

    @attr('functional_test')
    def test_delete_subject_type(self):
        subject_type = random_string(5)
        subject_type_page = self.page
        subject_type_page.click_on_accordian_link()
        subject_type_page.successfully_add_entity_type_with(subject_type)

        subject_page = subject_type_page.select_subject_type(subject_type)
        subject_page.wait_for_processing()
        add_subjects_page = subject_page.navigate_to_register_subject_page()
        add_subjects_page.add_subject_with(SUBJECT_DATA_WITHOUT_UNIQUE_ID)
        add_subjects_page.submit_subject()
        add_subjects_page.navigate_to_all_subjects()

        subject_type_page.click_subject_type(subject_type)
        subject_type_page.select_delete_action(confirm=True)
        message = subject_type_page.get_message()
        self.assertEqual(message, SUCCESSFULLY_DELETED_SUBJECT_TYPE_MSG)

        subject_type_page.click_on_accordian_link()
        subject_type_page.successfully_add_entity_type_with(subject_type)
        subject_page = subject_type_page.select_subject_type(subject_type)
        subject_page.wait_for_processing()
        self.assertTrue(subject_page.empty_table_text_visible())






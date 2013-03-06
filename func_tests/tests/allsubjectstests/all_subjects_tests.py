import unittest
from nose.plugins.attrib import attr
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_ALL_SUBJECT
from tests.logintests.login_data import VALID_CREDENTIALS
from framework.base_test import setup_driver, teardown_driver
from pages.loginpage.login_page import LoginPage
from pages.allsubjectspage.all_subjects_page import AllSubjectsPage

@attr('suit_1')
class TestAllSubjects(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)
        cls.page = AllSubjectsPage(cls.driver)

    def setUp(self):
        self.driver.go_to(DATA_WINNER_ALL_SUBJECT)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @attr("functional_test")
    def test_should_check_uncheck_all_checkboxes_via_a_click_on_master_checkbox(self):
        all_subjects_page = self.page
        subject_type = "clinic"
        all_subjects_page.open_subjects_table_for_entity_type(subject_type)
        master_checkbox_clicked = all_subjects_page.click_checkall_checkbox_for_entity_type(subject_type)
        self.assertEqual(True, master_checkbox_clicked)

        checked_count = all_subjects_page.get_checked_subjects_for_entity_type(subject_type)
        all_subjects_count = all_subjects_page.get_number_of_subject_for_entity_type(subject_type)
        self.assertEqual(checked_count, all_subjects_count)

        all_subjects_page.click_checkall_checkbox_for_entity_type(subject_type)
        checked_count = all_subjects_page.get_checked_subjects_for_entity_type(subject_type)
        self.assertEqual(checked_count, 0)
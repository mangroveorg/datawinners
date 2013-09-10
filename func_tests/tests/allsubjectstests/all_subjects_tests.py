from time import sleep
import unittest
from nose.plugins.attrib import attr
from framework.base_test import setup_driver, teardown_driver
from pages.allsubjectspage.all_subjects_list_page import AllSubjectsListPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, url
from tests.logintests.login_data import VALID_CREDENTIALS


@attr('suit_1')
class TestSubjectsPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def check_pagination_size(self, subjects_page, size):
        self.assertTrue(size >= subjects_page.number_of_rows())
        self.assertEqual(size, subjects_page.selected_page_size())

    @attr('functional_test')
    def test_all_subjects_page(self):
        self.login_with(VALID_CREDENTIALS)
        self.driver.go_to(url("/entity/subjects/clinic/"))
        subjects_page = AllSubjectsListPage(self.driver)
        self.check_pagination_size(subjects_page, 25)

        subjects_page.set_page_size(10)
        self.check_pagination_size(subjects_page, 10)

        subjects_page.search("tes")

        self.check_pagination_size(subjects_page, 10)

        sleep(1)
        for row in subjects_page.rows():
            self.assertIn("tes",row.text.lower())

    def login_with(self, credential):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        LoginPage(self.driver).login_with(credential)

# vim: ai ts=4 sts=4 et sw=4utf-8
import unittest
from nose.plugins.attrib import attr
from framework.base_test import  setup_driver, teardown_driver
from framework.utils.data_fetcher import from_, fetch_
from framework.utils.common_utils import generateId
from pages.addsubjecttypepage.add_subject_type_page import AddSubjectTypePage
from pages.loginpage.login_page import LoginPage
from pages.addsubjectpage.add_subject_page import AddSubjectPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_ALL_SUBJECT
from tests.addsubjecttypetests.add_subject_type_data import *
from tests.logintests.login_data import VALID_CREDENTIALS

@attr('suit_1')
class TestAddSubjectType(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)
        cls.driver.go_to(DATA_WINNER_ALL_SUBJECT)
        cls.page = AddSubjectTypePage(cls.driver)

    def setUp(self):
        self.driver.refresh()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @attr('functional_test', 'smoke')
    def test_add_new_subject_type(self):
        add_subject_type_page = self.page
        add_subject_type_page.click_on_accordian_link()
        entity_type = VALID_ENTITY[ENTITY_TYPE] + generateId()
        all_subject_page = add_subject_type_page.successfully_add_entity_type_with(entity_type)
        self.assertTrue(all_subject_page.check_subject_type_on_page(entity_type))

    @attr('functional_test')
    def test_add_existing_subject_type(self):
        add_subject_type_page = self.page
        add_subject_type_page.click_on_accordian_link()
        add_subject_type_page.add_entity_type_with(ALREADY_EXIST_ENTITY[ENTITY_TYPE], wait=False)
        self.assertEqual(add_subject_type_page.get_error_message(), fetch_(ERROR_MESSAGE, from_(ALREADY_EXIST_ENTITY)))

    @attr('functional_test')
    def test_add_blank_subject_type(self):
        add_subject_type_page = self.page
        add_subject_type_page.click_on_accordian_link()
        add_subject_type_page.add_entity_type_with(BLANK[ENTITY_TYPE], wait=False)
        self.assertEqual(add_subject_type_page.get_error_message(), fetch_(ERROR_MESSAGE, from_(BLANK)))

    @attr('functional_test')
    def test_add_invalid_subject_type(self):
        add_subject_type_page = self.page
        add_subject_type_page.click_on_accordian_link()
        add_subject_type_page.add_entity_type_with(INVALID_ENTITY[ENTITY_TYPE], wait=False)
        self.assertEqual(add_subject_type_page.get_error_message(), fetch_(ERROR_MESSAGE, from_(INVALID_ENTITY)))

 
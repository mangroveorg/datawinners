# vim: ai ts=4 sts=4 et sw=4utf-8
from nose.plugins.attrib import attr
from django.test import Client

from framework.base_test import teardown_driver, HeadlessRunnerTest
from framework.utils.data_fetcher import from_, fetch_
from framework.utils.common_utils import generateId
from pages.addsubjecttypepage.add_subject_type_page import AddSubjectTypePage
from pages.allsubjectspage.all_subject_type_page import AllSubjectTypePage
from pages.loginpage.login_page import login
from testdata.test_data import DATA_WINNER_ALL_SUBJECT
from tests.subjecttypetests.add_subject_type_data import *


class TestAddSubjectType(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        login(cls.driver)
        cls.driver.go_to(DATA_WINNER_ALL_SUBJECT)
        cls.page = AddSubjectTypePage(cls.driver)

    def setUp(self):
        self.driver.refresh()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @attr('functional_test')
    def test_add_new_subject_type(self):
        add_subject_type_page = self.page
        entity_type = VALID_ENTITY[ENTITY_TYPE] + generateId()
        client = Client()
        client.login(username="tester150411@gmail.com", password="tester150411")
        client.post('/entity/type/create', data={'referer': 'subject', 'entity_type_regex': entity_type})
        add_subject_type_page.refresh()
        self.assertTrue(add_subject_type_page.check_subject_type_on_page(entity_type))

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


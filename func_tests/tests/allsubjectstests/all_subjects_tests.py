import json
from time import sleep

from django.test import Client
from nose.plugins.attrib import attr

from framework.base_test import teardown_driver, HeadlessRunnerTest
from pages.addsubjecttypepage.add_subject_type_page import AddSubjectTypePage
from pages.allsubjectspage.all_subjects_list_page import AllSubjectsListPage
from framework.utils.common_utils import by_id, random_string
from pages.allsubjectspage.subjects_page import SubjectsPage
from pages.loginpage.login_page import login
from testdata.test_data import url
from tests.allsubjectstests.all_subjects_data import SUBJECT_TYPE, SUBJECT_TYPE_WHITE_SPACES, ERROR_MSG_INVALID_ENTRY, SUBJECT_TYPE_SPL_CHARS, SUBJECT_TYPE_BLANK, ERROR_MSG_EMPTY_ENTRY
from tests.logintests.login_data import VALID_CREDENTIALS


class TestSubjectsPage(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation_page = login(cls.driver, VALID_CREDENTIALS)


    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def check_pagination_size(self, subjects_page, size):
        # +1 for the select all hidden row in the beginning of the table
        self.assertTrue(size+1 >= subjects_page.number_of_rows())
        self.assertEqual(size, subjects_page.selected_page_size())


    def add_subject_type(self, entity_type):
        all_subjects_page = SubjectsPage(self.driver)
        all_subjects_page.click_add_a_subject_type_link()
        all_subjects_page.add_entity_type_with(entity_type)


    @attr('functional_test')
    def test_all_subjects_page(self):
        self.driver.go_to(url("/entity/subjects/clinic/"))
        subjects_page = AllSubjectsListPage(self.driver)
        self.check_pagination_size(subjects_page, 25)

        subjects_page.set_page_size(10)
        self.check_pagination_size(subjects_page, 10)

        subjects_page.search("tes")

        self.check_pagination_size(subjects_page, 10)

        sleep(1)
        for row in subjects_page.rows()[1:]:
            self.assertIn("tes", row.text.lower())

    def add_subject_type_all(self, entity_type):
        client = Client()
        client.login(username="tester150411@gmail.com", password="tester150411")
        response = client.post('/entity/type/create', data={'referer': 'subject', 'entity_type_regex': entity_type})
        response_dict = json.loads(response.content)
        return response_dict

    @attr('functional_test')
    def test_add_duplicate_subjectType(self):
        self.driver.go_to(url("/entity/subjects/"))
        subjects_page = AddSubjectTypePage(self.driver)
        subject_type_name = SUBJECT_TYPE + random_string(3)
        response = subjects_page.add_subject_type(subject_type_name)
        self.driver.go_to(url("/entity/subjects/"))
        self.validate_subject_type(subject_type_name)
        response = subjects_page.add_subject_type(subject_type_name)
        self.assertEqual(response['message'], subject_type_name+" already exists.")

    def validate_error_messages(self,subject_type_name):
        error_msg = self.driver.find(by_id("type_message")).text
        self.assertEquals(error_msg, subject_type_name)

    @attr('functional_test')
    def test_add_invalid_subjectType(self):
        self.driver.go_to(url("/entity/subjects/"))
        subjects_page = AddSubjectTypePage(self.driver)
        response = subjects_page.add_subject_type(SUBJECT_TYPE_WHITE_SPACES)
        self.assertEqual(response['message'], ERROR_MSG_INVALID_ENTRY)

        self.driver.go_to(url("/entity/subjects/"))
        subjects_page = AddSubjectTypePage(self.driver)
        response = subjects_page.add_subject_type(SUBJECT_TYPE_SPL_CHARS)
        self.assertEqual(response['message'], ERROR_MSG_INVALID_ENTRY)

        self.driver.go_to(url("/entity/subjects/"))
        subjects_page = AddSubjectTypePage(self.driver)
        response = subjects_page.add_subject_type(SUBJECT_TYPE_BLANK)
        self.assertEqual(response['message'], ERROR_MSG_EMPTY_ENTRY)

    def validate_subject_type(self, subject_type):
        element = self.driver.find_element_by_link_text(subject_type).text
        self.assertEquals(element.lower(), subject_type.lower())



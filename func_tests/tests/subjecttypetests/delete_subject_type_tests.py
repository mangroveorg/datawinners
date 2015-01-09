# vim: ai ts=4 sts=4 et sw=4utf-8
import json

from nose.plugins.attrib import attr
import requests
from requests.auth import HTTPDigestAuth

from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import random_string, by_css
from pages.addsubjecttypepage.add_subject_type_page import AddSubjectTypePage
from pages.loginpage.login_page import login
from testdata.test_data import DATA_WINNER_ALL_SUBJECT, url
from tests.addsubjecttests.add_subject_data import SUBJECT_DATA_WITHOUT_UNIQUE_ID
from tests.subjecttypetests.add_subject_type_data import *


class TestDeleteSubjectType(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.DIGEST_CREDENTIALS = HTTPDigestAuth('tester150411@gmail.com', 'tester150411')
        login(cls.driver)

    def setUp(self):
        self.driver.go_to(DATA_WINNER_ALL_SUBJECT)
        self.page = AddSubjectTypePage(self.driver)
        self.driver.refresh()

    def get_all_subjects_types(self):
        all_subject_elements = self.driver.find_elements_(by_css('tr td:nth-child(2) a'))
        return [subject.text for subject in all_subject_elements]

    def get_data_by_uri(self, uri):
        http_response = requests.get(url(uri), auth=self.DIGEST_CREDENTIALS)
        return json.loads(http_response.content)

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

    def _verify_entity_action(self, subject_type):
        subjects_deleted = json.loads(requests.get(url('/api/entity/actions/'), auth=self.DIGEST_CREDENTIALS).content)
        deleted_subjects = [dict for dict in subjects_deleted if
                            dict['entity_type'] == subject_type and dict['action'] == 'hard-delete']
        self.assertEqual(len(deleted_subjects), 1)

    @attr('functional_test')
    def test_delete_subject_type(self):
        subject_type = random_string(5)
        subject_type_page = self.page
        response = subject_type_page.add_subject_type(subject_type)
        subject_type_page.refresh()

        subject_page = subject_type_page.select_subject_type(subject_type)
        subject_page.wait_for_processing()
        add_subjects_page = subject_page.navigate_to_register_subject_page()
        add_subjects_page.add_subject_with(SUBJECT_DATA_WITHOUT_UNIQUE_ID)
        add_subjects_page.submit_subject()
        add_subjects_page.navigate_to_all_subjects()

        subject_type_page.click_subject_type(subject_type)
        subject_type_page.select_delete_action(confirm=True)
        self.driver.wait_until_element_is_not_present(5, by_css("#type_message .ajax_loader_small"))
        message = subject_type_page.get_message()
        self.assertEqual(message, SUCCESSFULLY_DELETED_SUBJECT_TYPE_MSG)

        self.assertNotIn(subject_type, self.get_all_subjects_types())
        self._verify_entity_action(subject_type)

        subject_type_page.click_on_accordian_link()
        subject_type_page.successfully_add_entity_type_with(subject_type)
        subject_page = subject_type_page.select_subject_type(subject_type)
        subject_page.wait_for_processing()
        self.assertTrue(subject_page.empty_table_text_visible())







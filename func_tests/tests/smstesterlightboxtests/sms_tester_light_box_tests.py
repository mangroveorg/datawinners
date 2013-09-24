# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest

from nose.plugins.attrib import attr
from framework.base_test import setup_driver, teardown_driver
from framework.utils.common_utils import by_css
from framework.utils.data_fetcher import fetch_, from_
from pages.loginpage.login_page import LoginPage
from pages.projectspage.projects_page import ProjectsPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, url
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.smstesterlightboxtests.sms_tester_light_box_data import EXCEED_NAME_LENGTH, RESPONSE_MESSAGE, VALID_ORDERED_SMS_DATA
from tests.testsettings import UI_TEST_TIMEOUT


@attr('suit_3')
class TestSMSTesterLightBox(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()

        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        cls.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)


    @attr('functional_test')
    def test_sms_player_for_exceeding_word_length(self):
        # going on all project page
        all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page("clinic5 test project")
        self.sms_tester_page = project_overview_page.open_sms_tester_light_box()

        self.sms_tester_page.send_sms_with(EXCEED_NAME_LENGTH)
        self.wait_while_loading()
        self.assertEqual(self.sms_tester_page.get_response_message(),
                         fetch_(RESPONSE_MESSAGE, from_(EXCEED_NAME_LENGTH)))

    def wait_while_loading(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css("div#response_info"), True)

    @attr('functional_test')
    def test_successful_ordered_sms_submission(self):


        # going on all project page
        self.driver.go_to(url("/project/"))
        all_project_page = ProjectsPage(self.driver)
        project_overview_page = all_project_page.navigate_to_project_overview_page("clinic5 test project")
        self.sms_tester_page = project_overview_page.open_sms_tester_light_box()

        self.sms_tester_page.send_sms_with(VALID_ORDERED_SMS_DATA)
        self.wait_while_loading()
        self.assertEqual(self.sms_tester_page.get_response_message(),
                         fetch_(RESPONSE_MESSAGE, from_(VALID_ORDERED_SMS_DATA)))

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)


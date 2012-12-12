# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from unittest.case import skipUnless, skipIf, skip

from nose.plugins.attrib import attr
from nose.tools import nottest
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from nose.plugins.skip import SkipTest
from tests.smstesterlightboxtests.sms_tester_light_box_data import PROJECT_DATA, VALID_DATA2, EXCEED_NAME_LENGTH, RESPONSE_MESSAGE, SMS_WITH_UNICODE, PROJECT_DATA_WITH_ACTIVITY_REPORT, VALID_ORDERED_SMS_DATA, VALID_ORDERED_SMS_DATA_WITH_ACTIVITY_REPORT, VALID_DATA, PROJECT_NAME


class BasePrepare(BaseTest):
    @nottest
    def prerequisites_of_sms_tester_light_box(self, project_to_open):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(project_to_open)))
        return project_overview_page.open_sms_tester_light_box()

@attr('suit_3')
class TestSMSTesterLightBox(BasePrepare):

    @attr('functional_test', 'smoke')
    def test_successful_sms_submission(self):
        """
        Function to test the successful SMS submission
        """
        sms_tester_page = self.prerequisites_of_sms_tester_light_box(PROJECT_DATA)
        sms_tester_page.send_sms_with(VALID_DATA)
        self.assertEqual(sms_tester_page.get_response_message(), fetch_(RESPONSE_MESSAGE, from_(VALID_DATA)))

    @attr('functional_test')
    def test_sms_player_for_exceeding_word_length(self):
        sms_tester_page = self.prerequisites_of_sms_tester_light_box(PROJECT_DATA)
        sms_tester_page.send_sms_with(EXCEED_NAME_LENGTH)
        self.assertEqual(sms_tester_page.get_response_message(), fetch_(RESPONSE_MESSAGE, from_(EXCEED_NAME_LENGTH)))

    @attr('functional_test', 'smoke')
    def test_successful_sms_submission(self):
        sms_tester_page = self.prerequisites_of_sms_tester_light_box(PROJECT_DATA)
        sms_tester_page.send_sms_with(VALID_DATA2)
        self.assertEqual(sms_tester_page.get_response_message(), fetch_(RESPONSE_MESSAGE, from_(VALID_DATA2)))

    @SkipTest
    @attr('functional_test', 'smoke')
    def test_sms_submission_for_unicode(self):
        sms_tester_page = self.prerequisites_of_sms_tester_light_box(PROJECT_DATA)
        sms_tester_page.send_sms_with(SMS_WITH_UNICODE)
        self.assertEqual(sms_tester_page.get_response_message(), fetch_(RESPONSE_MESSAGE, from_(SMS_WITH_UNICODE)))

@attr('suit_3')
class TestOrderedSMSTesterLightBox(BasePrepare):

    @attr('functional_test')
    def test_successful_ordered_sms_submission(self):
        sms_tester_page = self.prerequisites_of_sms_tester_light_box(PROJECT_DATA)
        sms_tester_page.send_sms_with(VALID_ORDERED_SMS_DATA)
        self.assertEqual(sms_tester_page.get_response_message(), fetch_(RESPONSE_MESSAGE, from_(VALID_ORDERED_SMS_DATA)))

    @attr('functional_test')
    @skip
    def test_sms_submission_for_project_with_activity_report(self):
        sms_tester_page = self.prerequisites_of_sms_tester_light_box(PROJECT_DATA_WITH_ACTIVITY_REPORT)
        sms_tester_page.send_sms_with(VALID_ORDERED_SMS_DATA_WITH_ACTIVITY_REPORT)
        self.assertEqual(sms_tester_page.get_response_message(), fetch_(RESPONSE_MESSAGE, from_(VALID_ORDERED_SMS_DATA)))


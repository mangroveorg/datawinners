# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import datetime

from nose.plugins.attrib import attr

from framework.utils.data_fetcher import fetch_, from_
from pages.languagespage.account_wide_reply_sms_page import AccountWideSmsReplyPage
from pages.languagespage.customized_language_locator import SUBJECT_REG_WITH_INCORRECT_NUMBER_OF_RESPONSES_LOCATOR
from pages.loginpage.login_page import login
from testdata.test_data import ACCOUNT_MESSAGES_URL
from tests.smstestertests.sms_tester_data import *
from datawinners.tests.data import DEFAULT_TEST_ORG_ID, TRIAL_ACCOUNT_ORGANIZATION_ID
from datawinners.accountmanagement.models import Organization
from tests.submissionlogtests.submission_log_tests import send_sms_with
from framework.base_test import HeadlessRunnerTest


class TestSMSTester(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        languages_page = login(cls.driver).navigate_to_languages_page()
        account_wide_sms_reply_page = languages_page.navigate_to_account_message_Tab()
        account_wide_sms_reply_page.update_message_for_selector(SUBJECT_REG_WITH_INCORRECT_NUMBER_OF_RESPONSES_LOCATOR,
                                                                'Updated')
        account_wide_sms_reply_page.save_changes()
        assert account_wide_sms_reply_page.get_success_message() == 'Changes saved successfully.'
        cls.trial_organization = Organization.objects.get(org_id=TRIAL_ACCOUNT_ORGANIZATION_ID)
        cls.trial_org_message_tracker = cls.trial_organization._get_message_tracker(datetime.today())
        cls.incoming_sms_count_initial = cls.trial_org_message_tracker.incoming_sms_count
        cls.incoming_web_count_initial = cls.trial_org_message_tracker.incoming_web_count

    @classmethod
    def tearDownClass(cls):
        cls.driver.go_to(ACCOUNT_MESSAGES_URL)
        AccountWideSmsReplyPage(cls.driver).remove_appended_message_for_selector(
            SUBJECT_REG_WITH_INCORRECT_NUMBER_OF_RESPONSES_LOCATOR, 'Updated')
        HeadlessRunnerTest.tearDownClass()

    def tearDown(self):
        self.trial_org_message_tracker.incoming_sms_count = self.incoming_sms_count_initial
        self.trial_org_message_tracker.incoming_web_count = self.incoming_web_count_initial
        self.trial_org_message_tracker.save()

    @attr('functional_test')
    def test_sms_player_for_exceeding_word_length(self):
        self.assertEqual(send_sms_with(EXCEED_NAME_LENGTH), fetch_(ERROR_MSG, from_(EXCEED_NAME_LENGTH)))

    @attr('functional_test')
    def test_sms_player_for_addition_of_data_sender(self):
        """
        Function to test the registration of the reporter using sms submission with registered number
        """
        self.assertRegexpMatches(send_sms_with(REGISTER_DATA_SENDER),
                                 fetch_(SUCCESS_MESSAGE, from_(REGISTER_DATA_SENDER)))

    @attr('functional_test')
    def test_sms_player_for_addition_of_data_sender_from_unknown_number(self):
        self.assertEqual(send_sms_with(REGISTER_DATA_SENDER_FROM_UNKNOWN_NUMBER),
                         fetch_(ERROR_MSG, from_(REGISTER_DATA_SENDER_FROM_UNKNOWN_NUMBER)))

    @attr('functional_test')
    def test_sms_player_for_registration_of_new_subject(self):
        organization = Organization.objects.get(org_id=DEFAULT_TEST_ORG_ID)
        message_tracker_before = organization._get_message_tracker(datetime.today())
        response = send_sms_with(REGISTER_NEW_SUBJECT)
        self.assertTrue(
            fetch_(SUCCESS_MESSAGE, from_(REGISTER_NEW_SUBJECT)) in response)
        message_tracker_after = organization._get_message_tracker(datetime.today())
        self.assertEqual(message_tracker_before.incoming_sms_count + 1, message_tracker_after.incoming_sms_count)
        self.assertEqual(message_tracker_before.sms_registration_count + 1,
                         message_tracker_after.sms_registration_count)

    @attr('functional_test')
    def test_counters_for_trail_org_for_registration_of_new_subject_when_sms_limit_reached(self):
        message_tracker_before = self.trial_org_message_tracker
        message_tracker_before.incoming_sms_count = 50
        message_tracker_before.save()
        response = send_sms_with(REGISTER_NEW_SUBJECT_TRIAL_ACCOUNT)
        message_tracker_after = self.trial_organization._get_message_tracker(datetime.today())
        self.assertEqual(message_tracker_before.incoming_sms_count, message_tracker_after.incoming_sms_count)
        self.assertEqual(message_tracker_before.sms_registration_count, message_tracker_after.sms_registration_count)

    @attr('functional_test')
    def test_counters_for_trail_org_for_registration_of_new_subject_when_submission_limit_reached(self):
        message_tracker_before = self.trial_org_message_tracker
        message_tracker_before.incoming_web_count = 1000
        message_tracker_before.save()
        response = send_sms_with(REGISTER_NEW_SUBJECT_TRIAL_ACCOUNT)
        message_tracker_after = self.trial_organization._get_message_tracker(datetime.today())
        self.assertEqual(message_tracker_before.incoming_sms_count + 1, message_tracker_after.incoming_sms_count)
        self.assertEqual(message_tracker_before.sms_registration_count + 1,
                         message_tracker_after.sms_registration_count)

    @attr('functional_test')
    def test_counters_for_trail_org_for_new_submission_when_sms_limit_and_total_submission_limit_reached(self):
        message_tracker_before = self.trial_org_message_tracker
        message_tracker_before.incoming_sms_count = 50
        message_tracker_before.incoming_web_count = 950
        message_tracker_before.save()
        response = send_sms_with(NEW_SUBMISSION_TRIAL_ACCOUNT)
        message_tracker_after = self.trial_organization._get_message_tracker(datetime.today())
        self.assertEqual(message_tracker_before.incoming_sms_count, message_tracker_after.incoming_sms_count)

    @attr('functional_test')
    def test_counters_for_trail_org_for_new_submission_when_sms_limit_not_reached_and_total_submission_limit_reached(
            self):
        message_tracker_before = self.trial_org_message_tracker
        message_tracker_before.incoming_web_count = 1000
        message_tracker_before.save()
        response = send_sms_with(NEW_SUBMISSION_TRIAL_ACCOUNT)
        message_tracker_after = self.trial_organization._get_message_tracker(datetime.today())
        self.assertEqual(message_tracker_before.incoming_sms_count, message_tracker_after.incoming_sms_count)

    @attr('functional_test')
    def test_counters_for_trail_org_for_new_submission_when_neither_sms_limit_nor_total_submission_limit_is_reached(
            self):
        message_tracker_before = self.trial_org_message_tracker
        message_tracker_before.save()
        response = send_sms_with(NEW_SUBMISSION_TRIAL_ACCOUNT)
        message_tracker_after = self.trial_organization._get_message_tracker(datetime.today())
        self.assertEqual(message_tracker_before.incoming_sms_count + 1, message_tracker_after.incoming_sms_count)

    @attr('functional_test')
    def test_sms_player_for_registration_of_existing_subject_short_code(self):
        self.assertEqual(send_sms_with(REGISTER_EXISTING_SUBJECT_SHORT_CODE),
                         fetch_(ERROR_MSG, from_(REGISTER_EXISTING_SUBJECT_SHORT_CODE)))

    @attr('functional_test')
    def test_sms_player_for_registration_with_invalid_geo_code(self):
        self.assertEqual(send_sms_with(REGISTER_INVALID_GEO_CODE),
                         fetch_(ERROR_MSG, from_(REGISTER_INVALID_GEO_CODE)))

    @attr('functional_test')
    def test_sms_player_for_registration_with_incorrect_number_of_answers(self):
        self.assertEqual(fetch_(ERROR_MSG, from_(REGISTER_WITH_WRONG_NUMBER_OF_ANSWERS)),
                         send_sms_with(REGISTER_WITH_WRONG_NUMBER_OF_ANSWERS))

    @attr('functional_test')
    def test_sms_player_for_unregistered_subject_and_invalid_geo_code(self):
        self.assertEqual(send_sms_with(UNREGISTER_ENTITY_ID_AND_SOME_INVALID_DATA),
                         fetch_(ERROR_MSG, from_(UNREGISTER_ENTITY_ID_AND_SOME_INVALID_DATA)))

    @attr('functional_test')
    def test_should_not_allow_not_linked_datasender_to_submit_data(self):
        self.assertEqual(send_sms_with(UNAUTHORIZED_DATASENDER),
                         fetch_(ERROR_MSG, from_(UNAUTHORIZED_DATASENDER)))

    def _get_test_paid_org_message_tracker(self, paid_test_org):
        return paid_test_org._get_message_tracker(datetime.today())

    @attr('functional_test')
    def test_should_check_with_right_order(self):
        test_data = MULTIPLE_WRONG_DATA.copy()
        paid_test_org = Organization.objects.get(org_id=DEFAULT_TEST_ORG_ID)
        self.assertEqual(send_sms_with(test_data),
                         "Error. You are not registered as a Data Sender. Please contact your supervisor.")

        test_data.update({SENDER: "2619876"})
        msg = send_sms_with(test_data)
        self.assertEqual(msg,
                         "Error. Questionnaire Code wrcode is incorrect. Find the Code on the top of the printed Questionnaire and resend SMS starting with this Code.")

        message = fetch_(SMS, from_(test_data))
        test_data.update({SMS: message.replace("wrcode", "cli002")})
        count_before_submission = (self._get_test_paid_org_message_tracker(paid_test_org)).incoming_sms_count
        self.assertEqual(send_sms_with(test_data),
                         "Error. You are not authorized to submit data for this Questionnaire. Please contact your supervisor.")
        self.assertEqual(count_before_submission + 1,
                         self._get_test_paid_org_message_tracker(paid_test_org).incoming_sms_count)

        test_data.update({SENDER: "1234567890"})
        count_before_submission = (self._get_test_paid_org_message_tracker(paid_test_org)).incoming_sms_count
        self.assertEqual(send_sms_with(test_data),
                         "Error. Incorrect number of responses. Please review printed Questionnaire and resend entire SMS.")
        self.assertEqual(count_before_submission + 1,
                         self._get_test_paid_org_message_tracker(paid_test_org).incoming_sms_count)

        message = fetch_(SMS, from_(test_data))
        test_data.update({SMS: message.replace("extradata", "")})
        self.assertEqual(send_sms_with(test_data),
                         "Error. cid00x5 is not registered. Check the Identification Number and resend entire SMS or contact your supervisor.")

        message = fetch_(SMS, from_(test_data))
        test_data.update({SMS: message.replace("CID00X5", "CID005")})
        self.assertEqual(send_sms_with(test_data),
                         "Error. Incorrect answer for question 3. Please review printed Questionnaire and resend entire SMS.")

        message = fetch_(SMS, from_(test_data))
        test_data.update({SMS: message.replace("age", "56")})
        count_before_submission = (self._get_test_paid_org_message_tracker(paid_test_org)).incoming_sms_count
        self.assertEqual(send_sms_with(test_data),
                         "Thank you Shweta. We received your SMS.")
        self.assertEqual(count_before_submission + 1,
                         self._get_test_paid_org_message_tracker(paid_test_org).incoming_sms_count)



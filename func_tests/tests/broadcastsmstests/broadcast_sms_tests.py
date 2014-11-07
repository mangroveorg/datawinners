from nose.plugins.attrib import attr
import uuid
from django.test import Client
from framework.base_test import HeadlessRunnerTest
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, LOGOUT
from tests.broadcastsmstests.broadcast_sms_data import SMS_VALID_DATA, SMS_EXACT_ON_LIMIT_DATA, \
    ERROR_MESSAGE_MAX_LENGTH_10, MORE_THAN_100_NUMBER, ERROR_MESSAGE_MAX_LENGTH_11
from tests.logintests.login_data import VALID_CREDENTIALS, NIGERIA_ACCOUNT_CREDENTIAL
from tests.projects.customizedreplysmstests.customized_reply_sms_data import PROJECT_DATA, PROJECT_QUESTIONNAIRE_DATA


class TestBroadcastSMS(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.client = Client()
        cls.send_message_page = cls._navigate_to_send_message_page()
        # cls.client.login(username='tester150411@gmail.com', password='tester150411')

    @attr('functional_test')
    def test_retain_sms_content_after_unsuccessful_send(self):
        self.send_message_page.write_sms_content(SMS_VALID_DATA)
        self.send_message_page.click_send()
        self.assertEquals(self.send_message_page.get_sms_content(), SMS_VALID_DATA)

    @attr('functional_test')
    def test_exceed_sms_content_limitation(self):
        self.send_message_page.write_sms_content(SMS_EXACT_ON_LIMIT_DATA + "redundant data")
        self.assertEquals(self.send_message_page.get_sms_content(), SMS_EXACT_ON_LIMIT_DATA)

    @classmethod
    def _navigate_to_send_message_page(cls, project_name="clinic test project1", credential=VALID_CREDENTIALS):
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        cls.global_navigation = login_page.do_successful_login_with(credential)
        all_project_page = cls.global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(project_name)
        send_message_page = project_overview_page.navigate_send_message_tab()
        return send_message_page


    @attr('functional_test')
    def test_should_show_help_text_when_other_people_is_choosen(self):
        self.send_message_page.choose_type_other_people("0333333333")
        self.assertTrue(self.send_message_page.is_other_people_help_text_visible())


    @attr('functional_test')
    def test_should_show_warning_when_people_number_is_more_than_100(self):
        self.send_message_page.write_sms_content(SMS_VALID_DATA)
        self.send_message_page.choose_type_other_people(other_numbers=MORE_THAN_100_NUMBER)
        self.assertFalse(self.send_message_page.is_warning_shown())
        self.send_message_page.click_send()
        self.assertTrue(self.send_message_page.is_warning_shown())
        self.send_message_page.close_warning_dialog()

    @attr('functional_test')
    def test_should_limit_phone_number_to_10digits_for_other_organization(self):
        self.send_message_page.choose_type_other_people(other_numbers="1234567890123")
        self.send_message_page.click_send()
        self._test_phone_number_limit(self.send_message_page, ERROR_MESSAGE_MAX_LENGTH_10)


    @attr('functional_test')
    def test_should_limit_phone_number_to_11digits_with_nigeria_account(self):
        self.driver.go_to(LOGOUT)
        send_message_page = self._navigate_to_send_message_page(credential=NIGERIA_ACCOUNT_CREDENTIAL)
        self._test_phone_number_limit(send_message_page, ERROR_MESSAGE_MAX_LENGTH_11)


    def _test_phone_number_limit(self, send_message_page, expected_error_message):
        send_message_page.choose_type_other_people(other_numbers="1234567890123")
        send_message_page.click_send()
        error_message = send_message_page.get_other_people_number_error()
        self.assertEqual(error_message, expected_error_message)

    @attr('functional_test')
    def test_option_to_send_message_to_unregistered_datasender_should_be_present(self):
        self.driver.go_to(LOGOUT)
        send_message_page = self._navigate_to_send_message_page(project_name="Project which everyone can send in data")

        self.assertTrue(send_message_page.is_send_a_message_to_unregistered_present())

    @attr('functional_test')
    def test_should_verify_the_total_number_of_anonymous_and_linked_data_senders_to_questionnaire_(self):
        dashboard_page = self.global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        self.create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()
        self.create_questionnaire_page.create_questionnaire_with(PROJECT_DATA, PROJECT_QUESTIONNAIRE_DATA)
        questionnaire_code = self.create_questionnaire_page.get_questionnaire_code()
        overview_page = self.create_questionnaire_page.save_and_create_project_successfully()

        self.create_submissions(questionnaire_code)
        send_message_page = overview_page.navigate_send_message_tab()

        actual_number_of_recipients = send_message_page.get_number_of_recipients_text_for_unregistered_and_associated_data_senders()
        number_of_associated_data_senders = send_message_page.get_number_of_recipients_for_associated_data_senders()

        self.assertEquals(str(number_of_associated_data_senders + 1) + " recipient(s)",actual_number_of_recipients)

    def create_submissions(self, questionnaire_code):
        _from = "100"
        _to = "919880734937"
        message = questionnaire_code + " some_name 50 cid001"
        data = {"message": message, "from_msisdn": _from, "to_msisdn": _to, "message_id":uuid.uuid1().hex}
        self.client.post("/submission", data)

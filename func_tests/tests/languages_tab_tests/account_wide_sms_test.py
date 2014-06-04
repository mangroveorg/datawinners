# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import by_css
from pages.languagespage.customized_language_locator import ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR
from pages.languagespage.customized_languages_page import CustomizedLanguagePage
from pages.loginpage.login_page import login
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from testdata.test_data import DATA_WINNER_SMS_TESTER_PAGE, CUSTOMIZE_MESSAGES_URL

default_messages = [u'Error. You are not registered as a Data Sender. Please contact your supervisor.',
                        u'Error. Questionnaire Code {Submitted Questionnaire Code} is incorrect. Find the Code on the top of the printed Questionnaire and resend SMS starting with this C',
                        u'Thank you {Name of Data Sender}.We registered your {Identification Number Type} {Name of Identification Number} {Submitted Identification Number}.',
                        u'Error. {Submitted Identification Number} already exists. Register your {Identification Number Type} with a different Identification Number.']

class TestAccountWideSMS(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        login(cls.driver, landing_page="customizemessages/")

    def setUp(self):
        self.language_page = CustomizedLanguagePage(self.driver)

    def check_default_account_messages(self):
        messages = [r.get_attribute('value') for r in
                    self.driver.find_elements_(ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR)]
        self.assertListEqual(default_messages, messages)

    def test_default_messages(self):
        self.check_default_account_messages()

    def test_language_change_has_no_effect_on_account_wide_section(self):
        self.language_page = CustomizedLanguagePage(self.driver)
        self.language_page.select_language("French", wait_for_load=True)
        self.check_default_account_messages()

    def test_should_show_warning_message_when_account_message_edited(self):
        self.change_account_messages()
        self.driver.find(by_css("#global_subjects_link")).click()
        self.verify_warning_dialog_present()
        self.driver.find_visible_element(by_css(".cancel_button")).click()
        self.assertListEqual(["new message"]*4,  self.language_page.get_all_account_wide_messages())

        self.driver.find(by_css("#global_subjects_link")).click()
        self.verify_warning_dialog_present()
        self.driver.find_visible_element(by_css(".no_button")).click()

        self.driver.find(by_css("#global_languages_link")).click()
        self.language_page = CustomizedLanguagePage(self.driver)
        self.check_default_account_messages()

        self.change_account_messages()
        self.driver.find(by_css("#global_subjects_link")).click()
        self.verify_warning_dialog_present()
        self.driver.find_visible_element(by_css(".yes_button")).click()

        self.driver.find(by_css("#global_languages_link")).click()
        self.language_page = CustomizedLanguagePage(self.driver)
        self.assertListEqual(["new message"]*4,  self.language_page.get_all_account_wide_messages())

        self.language_page.set_message_boxes(default_messages,ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR)
        self.language_page.save_changes()

    def test_warning_and_error_conditions(self):
        self.change_account_messages()
        self.assertEquals(4,self.driver.find_visible_elements_(by_css(".account_message_warning_message")).__len__())
        self.assertListEqual([u'Any changes you make to this text will apply for all Data Senders.']*4, [e.text for e in self.driver.find_visible_elements_(by_css(".account_message_warning_message"))])
        self.clear_all_messages()
        self.assertListEqual([u'Enter reply SMS text.']*4, [e.text for e in self.driver.find_elements_(by_css(".validationText"))])
        [r.send_keys("a" * 170) for r in self.driver.find_elements_(ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR)]
        self.assertListEqual(["a" * 160] * 4, self.language_page.get_all_account_wide_messages())

    def test_modify_automatic_messages(self):
        self.change_account_messages()
        self.language_page.save_changes()
        self.language_page.refresh()
        self.assertListEqual(["new message"]*4,  self.language_page.get_all_account_wide_messages())
        self.language_page.set_message_boxes(default_messages,ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR)
        self.language_page.save_changes()

    def test_should_use_modified_account_wide_sms_messages_to_send_reply(self):
        new_custom_messages = [u'You are not a registered data sender. Please contact your admin.',
                        u'Error. Submitted Code {Submitted Questionnaire Code} is incorrect. Resend SMS starting with the right code',
                        u'Thanks {Name of Data Sender}.Your {Identification Number Type} {Name of Identification Number} {Submitted Identification Number} has been registered.',
                        u'Error. {Submitted Identification Number} already exists. Register {Identification Number Type} with a another Identification Number.']
        self.change_account_messages(messages=new_custom_messages)
        self.language_page.save_changes()

        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        sms_tester_page = SMSTesterPage(self.driver)

        incorrect_ds_number_data =  {"from": "4444444", "to": '919880734937', "sms": "qcode sender_name 45 cid001" }
        sms_tester_page.send_sms_with(incorrect_ds_number_data)
        message = sms_tester_page.get_response_message()
        self.assertEquals('You are not a registered data sender. Please contact your admin.',message)

        incorrect_qcode_data =  {"from": "1234123413", "to": '919880734937', "sms": "wrcode sender_name 45 cid001" }
        sms_tester_page.send_sms_with(incorrect_qcode_data)
        message = sms_tester_page.get_response_message()
        self.assertEquals('Error. Submitted Code wrcode is incorrect. Resend SMS starting with the right code',message)

        success_subject_registration_data =  {"from": "1234123413", "to": '919880734937', "sms": "peo fname lname location 4,4 898989898" }
        sms_tester_page.send_sms_with(success_subject_registration_data)
        success_message = sms_tester_page.get_response_message()
        #Assumes that the word before 'has been registered' is the identification number
        message = success_message.split()
        registered_short_code = message[message.index('has') -1]
        self.assertEquals('Thanks Tester.Your people lname '+registered_short_code+ ' has been registered.',success_message)

        error_subject_registration = {"from": "1234123413", "to": '919880734937', "sms": "peo fname lname location 4,4 898989898 "+ registered_short_code }
        sms_tester_page.send_sms_with(error_subject_registration)
        message = sms_tester_page.get_response_message()
        self.assertEquals('Error. '+ registered_short_code +' already exists. Register People with a another Identification Number.',message)

        self.driver.go_to(CUSTOMIZE_MESSAGES_URL)
        self.language_page = CustomizedLanguagePage(self.driver)
        self.change_account_messages(messages=default_messages)
        self.language_page.save_changes()


    def clear_all_messages(self):
        [r.clear() for r in self.driver.find_elements_(ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR)]


    def change_account_messages(self,messages=None):
        #TODO:Should be changed once system variables introduced.Now messages getting chopped on UI since it exceeds 160chars since system vars not considered
        self.clear_all_messages()
        messages = messages or ["new message"]*4
        for index, element in enumerate(self.driver.find_elements_(ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR)):
            element.send_keys(messages[index])

    def verify_warning_dialog_present(self):
        self.driver.find_visible_element(by_css(".ui-dialog-titlebar"))



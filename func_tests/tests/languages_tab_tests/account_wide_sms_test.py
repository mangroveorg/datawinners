# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import by_css
from pages.languagespage.customized_language_locator import ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR
from pages.languagespage.customized_languages_page import CustomizedLanguagePage
from pages.loginpage.login_page import login

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
        self.assertListEqual([u'Any changes you make to this text will apply for all Data Senders']*4, [e.text for e in self.driver.find_visible_elements_(by_css(".account_message_warning_message"))])
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

    def clear_all_messages(self):
        [r.clear() for r in self.driver.find_elements_(ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR)]

    def change_account_messages(self):
        self.clear_all_messages()
        [r.send_keys('new message') for r in self.driver.find_elements_(ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR)]

    def verify_warning_dialog_present(self):
        self.driver.find_visible_element(by_css(".ui-dialog-titlebar"))



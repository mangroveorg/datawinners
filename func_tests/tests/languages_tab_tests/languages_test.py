# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from selenium.common.exceptions import NoSuchElementException
import time
from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import by_css, by_id, random_string
from pages.languagespage.customized_language_locator import LANGUAGE_SAVE_BUTTON_LOCATOR, NEW_LANGUAGE_INPUT_BOX, ADD_NEW_LANG_CONFIRM_BUTTON, ADD_NEW_LANG_CANCEL_BUTTON, CUSTOMIZED_MESSAGE_TEXTBOXES_LOCATOR, \
    SUBMISSION_WITH_INCORRECT_NUMBER_OF_RESPONSES_LOCATOR, SUCCESS_SUBMISSION_MESSAGE_LOCATOR
from pages.languagespage.customized_languages_page import CustomizedLanguagePage
from pages.loginpage.login_page import login
from tests.testsettings import UI_TEST_TIMEOUT


default_en_messages = [u'Thank you {Name of Data Sender}. We received your SMS: {List of Answers}',
                        u'Error. Incorrect answer for question {Question Numbers for Wrong Answer(s)}. Please review printed Questionnaire and resend entire SMS.',
                        u'Error. Incorrect number of responses. Please review printed Questionnaire and resend entire SMS.',
                        u'Error. {Submitted Identification Number} is not registered. Check the Identification Number and resend entire SMS or contact your supervisor.',
                        u'Error. You are not authorized to submit data for this Questionnaire. Please contact your supervisor.']

class  TestLanguageTab(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        login(cls.driver, landing_page="customizemessages/")

    def setUp(self):
        self.language_page = CustomizedLanguagePage(self.driver)
        self.language_page.refresh()
        self.language_page = CustomizedLanguagePage(self.driver)


    def tearDown(self):
        self.language_page.select_language("English", wait_for_load=True)
        self.language_page.revert_customized_messages_to_default()
        self.language_page.save_changes()

    @attr('functional_test')
    def test_languages_tab(self):

        self.check_for_default_en_messages()

        self.language_page.select_language("French", wait_for_load=True)
        # self.language_page = CustomizedLanguagePage(self.driver)
        expected_fr_messages = [u"{Name of Data Sender}. Nous avons recu votre SMS: {List of Answers}",
                                u'Erreur. Reponse incorrecte pour la question {Question Numbers for Wrong Answer(s)}. Veuillez revoir le Questionnaire imprime et renvoyez tout le SMS.',
                                u'Erreur. Nombre de reponses incorrect. Veuillez revoir le Questionnaire imprime et renvoyez tout le SMS.',
                                u"Erreur. {Submitted Identification Number} n'est pas enregistre. Verifiez le Numero d'Identification et renvoyez SMS en entier ou contactez votre superviseur.",
                                u"Erreur. Vous n'etes pas autorise a soumettre des donnees pour ce Questionnaire. Contactez votre superviseur."]
        french_messages = self.language_page.get_all_customized_reply_messages()
        self.assertListEqual(expected_fr_messages, french_messages)

    def clear_all_errormessages(self):
        [r.clear() for r in self.driver.find_elements_(CUSTOMIZED_MESSAGE_TEXTBOXES_LOCATOR)]

    def check_for_default_en_messages(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, SUCCESS_SUBMISSION_MESSAGE_LOCATOR, True)
        english_messages = self.language_page.get_all_customized_reply_messages()
        self.assertListEqual(default_en_messages, english_messages)

    def verify_160_character_length_limit(self):
        self.clear_all_errormessages()
        [r.send_keys("a" * 170) for r in self.driver.find_elements_(CUSTOMIZED_MESSAGE_TEXTBOXES_LOCATOR)]
        self.assertListEqual(["a" * 160] * 5, self.language_page.get_all_customized_reply_messages())

    @attr('functional_test')
    def test_validations(self):
        self.language_page.clear_custom_message(SUBMISSION_WITH_INCORRECT_NUMBER_OF_RESPONSES_LOCATOR)
        self.assertListEqual(['Enter reply SMS text.'], [e.text for e in self.driver.find_elements_(by_css(".validationText"))])
        self.assertTrue("ui-state-disabled" in self.driver.find(LANGUAGE_SAVE_BUTTON_LOCATOR).get_attribute('class'))

        self.language_page.refresh()
        self.language_page = CustomizedLanguagePage(self.driver)
        self.check_for_default_en_messages()

        # self.verify_160_character_length_limit()

    @attr('functional_test')
    def test_modify_and_save(self):
        self.change_reply_messages()
        self.language_page.save_changes()
        self.language_page.refresh()
        self.language_page = CustomizedLanguagePage(self.driver)
        self.assertListEqual([msg + "new message" for msg in default_en_messages],  self.language_page.get_all_customized_reply_messages())

    def change_reply_messages(self):
        for element in self.driver.find_elements_(CUSTOMIZED_MESSAGE_TEXTBOXES_LOCATOR):
            self.language_page.update_custom_message("new message",element)

    def verify_warning_dialog_present(self):
        self.driver.find_visible_element(by_css(".ui-dialog-titlebar"))

    def is_warning_dialog_present(self):
        try:
            self.driver.find_visible_element(by_css(".ui-dialog-titlebar"))
            return True
        except IndexError:
            return False

    @attr('functional_test')
    def test_unsaved_warning_dialog(self):
        def click_identification_number_page():
            self.driver.find(by_css("#global_subjects_link")).click()

        self.change_reply_messages()
        click_identification_number_page()
        self.verify_warning_dialog_present()
        self.driver.find_visible_element(by_css(".cancel_button")).click()
        self.assertListEqual([msg + "new message" for msg in default_en_messages],  self.language_page.get_all_customized_reply_messages())

        click_identification_number_page()
        self.verify_warning_dialog_present()
        self.language_page.click_revert_changes_button()

        self.assertFalse(self.is_warning_dialog_present())
        self.driver.find(by_css("#global_languages_link")).click()
        self.language_page = CustomizedLanguagePage(self.driver)
        self.assertFalse(self.is_warning_dialog_present())
        self.language_page.wait_for_reply_messages_to_load()
        self.check_for_default_en_messages()

        self.change_reply_messages()
        click_identification_number_page()
        self.verify_warning_dialog_present()
        self.language_page.click_save_changes_button()

        self.driver.find(by_css("#global_languages_link")).click()
        self.driver.wait_for_page_load()
        self.language_page = CustomizedLanguagePage(self.driver)
        self.language_page.wait_for_reply_messages_to_load()
        self.assertListEqual([msg + "new message" for msg in default_en_messages],  self.language_page.get_all_customized_reply_messages())


    @attr('functional_test')
    def test_unsaved_warning_on_language_change(self):
        def change_language():
            self.language_page.select_language("French")
        self.change_reply_messages()
        change_language()
        self.verify_warning_dialog_present()
        self.driver.find_visible_element(by_css(".cancel_button")).click()
        self.assertListEqual([msg + "new message" for msg in default_en_messages],  self.language_page.get_all_customized_reply_messages())

        change_language()
        self.verify_warning_dialog_present()
        self.language_page.click_revert_changes_button()

        self.assertFalse(self.is_warning_dialog_present())
        self.language_page.refresh()
        self.language_page = CustomizedLanguagePage(self.driver)
        self.assertFalse(self.is_warning_dialog_present())
        self.language_page.wait_for_reply_messages_to_load()
        self.check_for_default_en_messages()

        self.change_reply_messages()
        change_language()
        self.verify_warning_dialog_present()
        self.language_page.click_save_changes_button()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css(".success-message-box"), True)

        self.language_page.refresh()
        self.driver.wait_for_page_load()
        self.language_page = CustomizedLanguagePage(self.driver)
        self.language_page.wait_for_reply_messages_to_load()
        self.assertListEqual([msg + "new message" for msg in default_en_messages],  self.language_page.get_all_customized_reply_messages())


    @attr('functional_test')
    def test_should_validate_add_new_language(self):
        self.language_page.add_new_language("")
        self.assertIn("Please enter a name for your language.", [e.text for e in self.driver.find_elements_(by_css(".validationText"))])

        self.driver.find_text_box(NEW_LANGUAGE_INPUT_BOX).enter_text("english")
        self.driver.find(ADD_NEW_LANG_CONFIRM_BUTTON).click()
        self.assertIn("english already exists.", [e.text for e in self.driver.find_elements_(by_css(".validationText"))])

        self.driver.find(ADD_NEW_LANG_CANCEL_BUTTON).click()

    @attr('functional_test')
    def test_dirty_dialog_behavior_for_add_new_language(self):
        self.change_reply_messages()
        self.language_page.select_add_new_language_option()
        self.assertTrue(self.is_warning_dialog_present())

        self.language_page.click_revert_changes_button()

        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_id("add_new_language_pop"))
        self.language_page.save_new_language("new_lang"+random_string(4))
        self.assertEquals("Your language has been added successfully. Please translate the suggested automatic reply SMS text.",
                          self.language_page.get_success_message())

        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".success-message-box"))
        self.assertFalse(self.is_warning_dialog_present())

        self.language_page.select_language("English", True)

        self.assertFalse(self.is_warning_dialog_present())
        self.check_for_default_en_messages()

        self.language_page = CustomizedLanguagePage(self.driver)
        self.change_reply_messages()
        self.language_page.select_add_new_language_option()
        self.assertTrue(self.is_warning_dialog_present())

        self.language_page.click_save_changes_button()
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".success-message-box"))
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_id("add_new_language_pop"))
        self.language_page.save_new_language("new_lang"+random_string(4))
        self.assertEquals("Your language has been added successfully. Please translate the suggested automatic reply SMS text.",
                          self.language_page.get_success_message())
        self.language_page.select_language("English", True)
        self.assertListEqual([msg + "new message" for msg in default_en_messages],  self.language_page.get_all_customized_reply_messages())

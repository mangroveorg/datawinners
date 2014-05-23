# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import by_css
from pages.languagespage.customized_languages_page import CustomizedLanguagePage
from pages.loginpage.login_page import login
from tests.testsettings import UI_TEST_TIMEOUT

default_en_messages = [u'Thank you {Name of Data Sender}. We received your SMS: {List of Answers}',
                        u'Error. Incorrect answer for question {Question Numbers for Wrong Answer(s)}. Please review printed Questionnaire and resend entire SMS.',
                        u'Error. Incorrect number of responses. Please review printed Questionnaire and resend entire SMS.',
                        u'Error. {Submitted Identification Number} is not registered. Check the Identification Number and resend entire SMS or contact your supervisor.',
                        u'You are not authorized to submit data for this Questionnaire. Please contact your supervisor.']

class TestLanguageTab(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        login(cls.driver, landing_page="languages/")
        cls.language_page = CustomizedLanguagePage(cls.driver)

    def test_languages_tab(self):

        self.check_for_default_en_messages()

        self.language_page.select_language("French", wait_for_load=True)

        expected_fr_messages = [u"{Nom de l'Exp\xe9diteur de Donn\xe9es}. Nous avons recu votre SMS: {Liste des R\xe9ponses}",
                                u'Erreur. Reponse incorrecte pour la question {Num\xe9ro(s) de la(des) Question(s) correspondant \xe0 la(aux) R\xe9ponse(s) Incorrecte(s)}. Veuillez revoir le Questionnaire imprime et renvoyez tout le SMS.',
                                u'Erreur. Nombre de reponses incorrect. Veuillez revoir le Questionnaire imprime et renvoyez tout le SMS.',
                                u"Erreur. {Num\xe9ro d'Identification Soumis} n'est pas enregistre. Verifiez le Numero d'Identification et renvoyez SMS en entier ou contactez votre superviseur.",
                                u"Vous n'etes pas autorise a soumettre des donnees pour ce Questionnaire. Contactez votre superviseur."]
        french_messages = [r.get_attribute('value') for r in self.driver.find_elements_(by_css("textarea"))]
        self.assertListEqual(expected_fr_messages, french_messages)

    def clear_all_errormessages(self):
        [r.clear() for r in self.driver.find_elements_(by_css("textarea"))]

    def check_for_default_en_messages(self):
        english_messages = [r.get_attribute('value') for r in self.driver.find_elements_(by_css("textarea"))]
        self.assertListEqual(default_en_messages, english_messages)

    def test_validations(self):
        self.clear_all_errormessages()
        self.language_page.save_changes()

        self.assertListEqual([u'Enter reply SMS text.']*5, [e.text for e in self.driver.find_elements_(by_css(".validationText"))])

        self.assertTrue("ui-state-disabled" in self.driver.find(by_css("#language_save")).get_attribute('class'))

        self.language_page.refresh()

        self.check_for_default_en_messages()

    def test_modify_and_save(self):

        [r.send_keys(' new') for r in self.driver.find_elements_(by_css("textarea"))]
        self.language_page.save_changes()
        self.language_page.refresh()
        self.assertListEqual([msg + " new" for msg in default_en_messages],  self.language_page.get_all_messages())

        self.language_page.set_message_boxes(default_en_messages)

        self.language_page.save_changes()

    def test_unsaved_warning_dialog(self):
        [r.send_keys(' new') for r in self.driver.find_elements_(by_css("textarea"))]
        self.driver.find(by_css("#global_subjects_link")).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css(".ui-dialog-titlebar"), True)
        self.driver.find(by_css("#cancel_language_changes_warning_dialog_section #cancel_dialog")).click()
        self.assertListEqual([msg + " new" for msg in default_en_messages],  self.language_page.get_all_messages())

        self.driver.find(by_css("#global_subjects_link")).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css(".ui-dialog-titlebar"), True)
        self.driver.find(by_css("#cancel_language_changes_warning_dialog_section #ignore_changes")).click()

        self.driver.find(by_css("#global_languages_link")).click()
        self.check_for_default_en_messages()

        [r.send_keys(' new') for r in self.driver.find_elements_(by_css("textarea"))]
        self.driver.find(by_css("#global_subjects_link")).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css(".ui-dialog-titlebar"), True)
        self.driver.find(by_css("#cancel_language_changes_warning_dialog_section #save_changes")).click()

        self.driver.find(by_css("#global_languages_link")).click()
        self.assertListEqual([msg + " new" for msg in default_en_messages],  self.language_page.get_all_messages())

        self.language_page.set_message_boxes(default_en_messages)
        self.language_page.save_changes()






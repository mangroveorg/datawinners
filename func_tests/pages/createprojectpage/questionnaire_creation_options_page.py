from time import sleep
from pages.createprojectpage.create_project_locator import CONTINUE_BTN
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.page import Page
from tests.questionnaireTemplateTests.questionnaire_template_test_data import BLANK_QUESTIONNAIRE_SELECTION_ACCORDION, SELECT_USING_TEMPLATE_ACCORDION, AJAX_LOADER_HORIZONTAL, TEMPLATE_CATEGORY_ACCORDION, SELECTED_TEMPLATE_QUESTIONS_DIV, TEMPLATE_NAME_DIV, TEMPLATE_NAME_HEADER, TEMPLATE_QUESTIONS
from tests.testsettings import UI_TEST_TIMEOUT


class QuestionnaireCreationOptionsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)


    def select_blank_questionnaire_creation_option(self):
        blank_questionnaire_accoridion = self.driver.find_element_by_xpath(BLANK_QUESTIONNAIRE_SELECTION_ACCORDION)
        blank_questionnaire_accoridion.click()
        sleep(1)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, CONTINUE_BTN, True)
        return self.go_to_create_questionnaire_page()

    def go_to_create_questionnaire_page(self):
        self.driver.find(CONTINUE_BTN).click()
        return CreateQuestionnairePage(self.driver)

    def select_create_questionnaire_by_template_option(self):
        create_by_template_option = self.driver.find_element_by_xpath(SELECT_USING_TEMPLATE_ACCORDION)
        create_by_template_option.click()
        sleep(1)
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, AJAX_LOADER_HORIZONTAL)
        self.driver.find(TEMPLATE_CATEGORY_ACCORDION).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, TEMPLATE_NAME_DIV, True)
        self.driver.find(TEMPLATE_NAME_DIV).click()
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, AJAX_LOADER_HORIZONTAL)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, SELECTED_TEMPLATE_QUESTIONS_DIV, True)

    def continue_to_questionnaire_page(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, CONTINUE_BTN, True)
        self.driver.find(CONTINUE_BTN).click()
        return CreateQuestionnairePage(self.driver)

    def get_template_name(self):
        return self.driver.find(TEMPLATE_NAME_HEADER).text

    def get_template_questions(self):
        questions = []
        question_divs = self.driver.find_elements_(TEMPLATE_QUESTIONS)
        for question in question_divs:
            questions.append(question.text)
        return questions
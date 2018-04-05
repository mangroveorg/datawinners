from time import sleep
from pages.createprojectpage.create_project_locator import *
from pages.globalnavigationpage.global_navigation_locator import CREATE_PROJECT_LINK
from pages.questionnairetabpage.questionnaire_tab_page import QuestionnaireTabPage
from pages.page import Page
from tests.questionnaireTemplateTests.questionnaire_template_test_data import BLANK_QUESTIONNAIRE_SELECTION_ACCORDION, SELECT_USING_TEMPLATE_ACCORDION, AJAX_LOADER_HORIZONTAL, TEMPLATE_CATEGORY_ACCORDION, SELECTED_TEMPLATE_QUESTIONS_DIV, TEMPLATE_NAME_DIV, TEMPLATE_NAME_HEADER, TEMPLATE_QUESTIONS,\
    POLL_QUESTIONNAIRE_SELECTION_ACCORDION
from tests.testsettings import UI_TEST_TIMEOUT


class QuestionnaireCreationOptionsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)


    def select_blank_questionnaire_creation_option(self):
        sleep(1)
        blank_questionnaire_accoridion = self.driver.find(by_css(BLANK_QUESTIONNAIRE_SELECTION_ACCORDION))
        blank_questionnaire_accoridion.click()
        sleep(1)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, CONTINUE_BTN, True)
        return self.go_to_create_questionnaire_page()

    def select_poll_questionnaire_option(self):
        try:
            self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css(POLL_QUESTIONNAIRE_SELECTION_ACCORDION), True)
        except Exception as e:
            self.driver.create_screenshot("debug-ft-impossible-to-create-poll")
            raise e
        blank_questionnaire_accoridion = self.driver.find(by_css(POLL_QUESTIONNAIRE_SELECTION_ACCORDION))
        blank_questionnaire_accoridion.click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, CONTINUE_BTN, True)
        return self.go_to_create_questionnaire_page()

    def go_to_create_questionnaire_page(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, CONTINUE_BTN)
        self.driver.find(CONTINUE_BTN).click()
        return QuestionnaireTabPage(self.driver)

    def select_create_questionnaire_by_template_option(self):
        create_by_template_option = self.driver.find(by_css(SELECT_USING_TEMPLATE_ACCORDION))
        create_by_template_option.click()
        sleep(1)
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, AJAX_LOADER_HORIZONTAL)
        self.driver.find(TEMPLATE_CATEGORY_ACCORDION).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, TEMPLATE_NAME_DIV, True)
        self.driver.find(TEMPLATE_NAME_DIV).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, SELECTED_TEMPLATE_QUESTIONS_DIV, True)

    def get_questions_list_for_selected_project(self, project_name):
        self.click_copy_existing_questionnaire()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_id("existing_questionnaires"), True)
        self.driver.find(by_xpath(".//*[@id='existing_questionnaires']/div/div[text()='%s']" % project_name)).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_id("existing_questions"), True)
        questions_list = self.driver.find_elements_(by_css('#existing_questions li'))
        return [question.text for question in questions_list]

    def get_project_list(self):
        create_by_template_option = self.driver.find(by_id("copy_existing_questionnaire"))
        create_by_template_option.click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_id("existing_questionnaires"), True)
        projects = self.driver.find_elements_(by_css(".questionnaire_data div.highlight_on_hover"))
        return [project.text for project in projects]

    def continue_to_questionnaire_page(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, CONTINUE_BTN, True)
        self.driver.find(CONTINUE_BTN).click()
        return QuestionnaireTabPage(self.driver)

    def get_template_name(self):
        return self.driver.find(TEMPLATE_NAME_HEADER).text

    def get_template_questions(self):
        questions = []
        question_divs = self.driver.find_elements_(TEMPLATE_QUESTIONS)
        for question in question_divs:
            questions.append(question.text)
        return questions

    def click_copy_existing_questionnaire(self):
        create_by_template_option = self.driver.find(COPY_EXISTING_QUESTIONNAIRE_LINK_LOCATOR)
        create_by_template_option.click()

    def count_questionnaires_available_for_copy(self):
        self.click_copy_existing_questionnaire()
        return len(self.driver.find_elements_(QUESTIONNAIRES_LIST_LOCATOR))
from time import sleep
from framework.utils.common_utils import by_css, by_xpath
from pages.createprojectpage.create_project_locator import CONTINUE_BTN
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT


class QuestionnaireCreationOptionsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)


    def select_blank_questionnaire_creation_option(self):
        blank_questionnaire_accoridion = self.driver.find_element_by_xpath(".//*[@id='questionnaire_types']/div[1]/span[2]")
        blank_questionnaire_accoridion.click()
        sleep(1)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, CONTINUE_BTN, True)
        self.driver.find(CONTINUE_BTN).click()
        return CreateQuestionnairePage(self.driver)

    def select_create_questionnaire_by_template_option(self):
        create_by_template_option = self.driver.find_element_by_xpath(".//*[@id='questionnaire_types']/div[4]/span[2]")
        create_by_template_option.click()
        sleep(1)
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css('.ajax-loader'))
        self.driver.find(by_css('#questionnaire_template .template_data')).click()
        self.driver.find(by_css('#questionnaire_template .template_name')).click()

        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css('.selected_questions'), True)

        self.driver.wait_for_element(UI_TEST_TIMEOUT, CONTINUE_BTN, True)
        self.driver.find(CONTINUE_BTN).click()
        return CreateQuestionnairePage(self.driver)





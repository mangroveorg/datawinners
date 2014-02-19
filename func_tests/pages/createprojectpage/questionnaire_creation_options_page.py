from framework.utils.common_utils import by_css
from pages.createprojectpage.create_project_locator import CONTINUE_BTN
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT


class QuestionnaireCreationOptionsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)


    def select_blank_questionnaire_creation_option(self):
        blank_questionnaire_accoridion = self.driver.find_elements_(by_css('.questionnaire_type_header'))[0]
        blank_questionnaire_accoridion.click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, CONTINUE_BTN, True)
        self.driver.find(CONTINUE_BTN).click()
        return CreateQuestionnairePage(self.driver)




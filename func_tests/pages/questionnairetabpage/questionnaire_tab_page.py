from framework.utils.common_utils import by_css
from pages.page import Page


class QuestionnaireTabPage(Page):

    def __init__(self, driver):
        Page.__init__(self, driver)

    def get_questionnaire_title(self):
        return self.driver.find_text_box(by_css(".project_title")).text

    def get_existing_questions_count(self):
        return len(self.driver.find_elements_(by_css("#qns_list li")))

    def get_existing_question_list(self):
        questions = self.driver.find_elements_(by_css("#qns_list li > a"))
        return [question.text for question in questions]





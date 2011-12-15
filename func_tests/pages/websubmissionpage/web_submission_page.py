from framework.utils.data_fetcher import from_, fetch_
from pages.page import Page
from pages.websubmissionpage.web_submission_locator import *
from tests.websubmissiontests.web_submission_data import LABEL, ANSWER

class WebSubmissionPage(Page):

    def __init__(self, driver):
        Page.__init__(self, driver)

    def submit_questionnaire_with(self, answers):
        for i in range(4):
            self.driver.find_text_box(get_by_css_name("input", fetch_(LABEL, from_(answers[i])))).enter_text(fetch_(ANSWER,from_(answers[i])))
        self.driver.find_drop_down(get_by_css_name("select", fetch_(LABEL, from_(answers[4])))).set_selected(fetch_(ANSWER,from_(answers[4])))
        checkboxes = self.driver.find_elements_(get_by_css_name("input", fetch_(LABEL, from_(answers[5]))))
        checkboxes[0].click()
        checkboxes[2].click()
        self.driver.find_text_box(get_by_css_name("input", fetch_(LABEL, from_(answers[6])))).enter_text(fetch_(ANSWER,from_(answers[6])))
        self.driver.find(SUBMIT_BTN).click()

    def get_errors(self):
        errors =  self.driver.find_elements_(QUESTIONS_WITH_ERRORS)
        error_messages=[self.describe_error(error_element) for error_element in errors]
        return error_messages

    def describe_error(self, error_element):
        question = error_element.find_element_by_xpath('../../../h6').text
        return {question: error_element.text}

    def get_trial_web_limit_alert(self):
        return self.driver.find_elements_(TRIAL_WEB_LIMIT_REACHED_WARNING_BOX)[0].text


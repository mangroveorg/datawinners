from pages.page import Page
from pages.warningdialog.warning_dialog_page import WarningDialog
from pages.websubmissionpage.web_submission_locator import *
from tests.websubmissiontests.web_submission_data import *


class WebSubmissionPage(Page):

    def __init__(self, driver):
        Page.__init__(self, driver)
        self.submit_answer_for = {TEXT : self.type_text, SELECT: self.select_option, CHECKBOX: self.select_checkbox}

    def fill_questionnaire_with(self, answers):
        for answer in answers:
            self.submit_answer_for[answer[TYPE]](answer)

    def submit_answers(self):
        self.driver.find(SUBMIT_BTN).click()
        return self

    def get_errors(self):
        errors =  self.driver.find_elements_(QUESTIONS_WITH_ERRORS)
        error_messages=[self.describe_error(error_element) for error_element in errors]
        return error_messages

    def describe_error(self, error_element):
        question = error_element.find_element_by_xpath('../../../h6').text
        return {question: error_element.text}

    def get_trial_web_limit_alert(self):
        return self.driver.find_elements_(TRIAL_WEB_LIMIT_REACHED_WARNING_BOX)[0].text

    def select_option(self, data):
        self.driver.find_drop_down(by_css("select#id_%s" % data[QCODE])).set_selected_by_text(data[ANSWER])

    def select_checkbox(self, data):
        for answer in data[ANSWER]:
            self.driver.find(by_css("input[id^='id_%s'][value='%s']" % (data[QCODE], answer))).click()

    def type_text(self, data):
        self.driver.find_text_box(by_css("input#id_%s" % data[QCODE])).enter_text(data[ANSWER])

    def get_title(self):
        return self.driver.get_title()

    def get_section_title(self):
        return self.driver.find(SECTION_TITLE).text

    def get_project_name(self):
        return self.driver.find(PROJECT).text

    def go_back_to_project_list(self):
        self.driver.find(BACK_TO_PROJECT_LINK).click()

    def cancel_submission(self):
        self.driver.find(by_css("#cancel")).click()
        return WarningDialog(self.driver)
from pages.datasenderpage.data_sender_locator import SMARTPHONE_NAV
from pages.page import Page
from pages.smartphoneinstructionpage.smart_phone_instruction_page import SmartPhoneInstructionPage
from pages.submissionlogpage.submission_log_page import SubmissionLogPage
from pages.warningdialog.warning_dialog import WarningDialog
from pages.websubmissionpage.web_submission_locator import *
from tests.testsettings import UI_TEST_TIMEOUT
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

    def get_success_message(self):
        Success_Message_Box = by_xpath("//div[contains(@class,'success-message-box') and not(contains(@class,'none'))]")
        self.driver.wait_for_element(UI_TEST_TIMEOUT, Success_Message_Box, True)
        return self.driver.find(Success_Message_Box).text

    def describe_error(self, error_element):
        question = error_element.find_element_by_xpath('../../../h6').text
        return {question: error_element.text}

    def get_trial_web_limit_alert(self):
        return self.driver.find_elements_(TRIAL_WEB_LIMIT_REACHED_WARNING_BOX)[0].text

    def select_option(self, data):
        self.driver.find_drop_down(by_css("select#id_%s" % data[QCODE])).set_selected_by_text(data[ANSWER])

    def select_checkbox(self, data):
        for answer in data[ANSWER]:
            self.driver.find(by_css("input[name='%s'][value='%s']" % (data[QCODE], answer))).click()

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
        self.driver.find(CANCEL).click()
        return WarningDialog(self.driver)

    def navigate_to_project_list(self):
        self.driver.find(BACK_TO_PROJECT_LINK).click()

    def navigate_to_smart_phone_instruction(self):
        self.driver.find(SMARTPHONE_NAV).click()
        return SmartPhoneInstructionPage(self.driver)

    def fill_and_submit_answer(self, answers):
        self.fill_questionnaire_with(answers)
        self.submit_answers()

    def get_questions_and_instructions(self):
        labels, instructions = [], []
        for question in self.driver.find(by_css("form ol.que_width")).find_elements(by="css selector", value="li h6"):
            labels.append(question.text)
        for question in self.driver.find(by_css("form ol.que_width")).find_elements(by="css selector", value="li p.instructions"):
            if question.get_attribute("id"):
                instructions.append(question.text)
        return labels, instructions

    def navigate_to_submission_log(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_id('submission_log_link'), True).click()
        return SubmissionLogPage(self.driver)

    def get_text_value(self, qcode):
        return self.driver.find(by_css("input#id_%s" % qcode)).get_attribute('value')
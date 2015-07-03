from framework.utils.common_utils import by_css, by_id, generateId, by_xpath
from pages.createquestionnairepage.create_questionnaire_locator import POLL_SMS_DROPDOWN, \
    POLL_VIA_SMS_RD_BUTTON, SMS_TEXTBOX, CREATE_POLL_BUTTON, POLL_TITLE, DATA_SENDER_TAB, POLL_TAB, DATA_TAB_BTN, \
    POLL_VIA_BROADCAST_RD_BUTTON, poll_info_accordian, deactivate_link, POLL_STATUS_INFO, \
    AUTOMATIC_REPLY_ACCORDIAN, POLL_SMS_ACCORDIAN, AUTOMATIC_REPLY_SMS_TEXT, ITALIC_GREY_COMMENT, \
    POLL_SMS_TABLE, SEND_SMS_LINK, PROJECT_LANGUAGE, SAVE_LANG_BTN, SUCCESS_MSG_BOX, \
    DEACTIVATE_BTN, ON_SWITCH, RECIPIENT_DROPDOWN, SEND_BUTTON, CANCEL_SMS, LANGUAGE_TEXT, ACTIVATE_BTN, activate_link, \
    ACTIVE_POLL_NAME, POLL_INFORMATION_BOX, ON_OFF_SWITCH
from pages.globalnavigationpage.global_navigation_locator import PROJECT_LINK
from pages.page import Page
from tests.projects.questionnairetests.project_questionnaire_data import POLL, POLL_RECIPIENTS, MY_POLL_RECIPIENTS, DATA_ANALYSIS
from tests.testsettings import UI_TEST_TIMEOUT

class PollQuestionnairePage(Page):

    def __init__(self, driver):
        Page.__init__(self, driver)

    def select_sms_option(self):
        self.driver.find_radio_button(POLL_VIA_SMS_RD_BUTTON).click()

    def select_broadcast_option(self):
        self.driver.find_radio_button(POLL_VIA_BROADCAST_RD_BUTTON).click()

    def enter_sms_text(self):
        self.driver.find_text_box(SMS_TEXTBOX).enter_text("what"+generateId()+"?")

    def select_receipient(self, recipient_type, receipient_name):
        self.select_recipient_type(POLL_SMS_DROPDOWN, recipient_type)
        self._configure_given_contacts(receipient_name)

    def select_recipient_type(self, dropdown, recipient_type):
        self.driver.find_drop_down(dropdown).set_selected(recipient_type)

    def click_create_poll(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, CREATE_POLL_BUTTON, True)
        self.driver.find(CREATE_POLL_BUTTON).click()

    def is_poll_created(self, poll_title):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, POLL_TITLE, True)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, DATA_SENDER_TAB, True)
        return (self.driver.find(POLL_TITLE).text == poll_title) & self.are_all_tabs_loaded()

    def are_all_tabs_loaded(self):
        data_tab = self.driver.find(DATA_TAB_BTN).text == DATA_ANALYSIS
        data_senders_tab = self.driver.find(DATA_SENDER_TAB).text == POLL_RECIPIENTS
        poll_tab = self.driver.find(POLL_TAB).text == POLL
        return data_tab & data_senders_tab & poll_tab

    def does_poll_has_broacast_accordians(self, poll_title):
        data_tab = self.driver.find(DATA_TAB_BTN).text == DATA_ANALYSIS
        poll_tab = self.driver.find(POLL_TAB).text == POLL
        return (self.driver.find(POLL_TITLE).text == poll_title) & data_tab & poll_tab

    def is_poll_status_accordian_present(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, POLL_STATUS_INFO, True)
        self.driver.find(POLL_STATUS_INFO).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, ITALIC_GREY_COMMENT, True)
        return self.driver.find(ITALIC_GREY_COMMENT).text != ''

    def is_automatic_reply_sms_option_present(self):
        self.select_element(AUTOMATIC_REPLY_ACCORDIAN)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, LANGUAGE_TEXT, True)
        return self.driver.find(LANGUAGE_TEXT).text == AUTOMATIC_REPLY_SMS_TEXT

    def is_sent_poll_sms_table(self):
        self.select_element(POLL_SMS_ACCORDIAN)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, POLL_SMS_TABLE, True)
        return self.driver.find(POLL_SMS_TABLE) is not None

    def change_automatic_reply_sms_language(self, language):
        try:
            self.select_element(POLL_TAB)
            self.select_element(AUTOMATIC_REPLY_ACCORDIAN)
            self.driver.wait_for_element(UI_TEST_TIMEOUT, ON_SWITCH, True)
            self.driver.find_drop_down(PROJECT_LANGUAGE).set_selected(language)
            self.driver.find_text_box(SAVE_LANG_BTN).click()
            return True
        except:
            return False

    def get_automatic_reply_status(self):
        automatic_reply_status = self.driver.find(AUTOMATIC_REPLY_ACCORDIAN).text
        reply_status_list = automatic_reply_status.split()
        status = reply_status_list[len(reply_status_list) - 1]
        return status

    def is_reply_sms_language_updated(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, SUCCESS_MSG_BOX, True)
        return self.driver.find(SUCCESS_MSG_BOX) is not None

    def change_autoamtic_reply_sms_status(self):
        self.select_element(POLL_TAB)
        self.select_element(AUTOMATIC_REPLY_ACCORDIAN)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, ON_OFF_SWITCH)
        self.select_element(ON_OFF_SWITCH)
        self.select_element(SAVE_LANG_BTN)

    def are_all_three_accordians_present(self):
        try:
            self.driver.find(POLL_TAB).click()
            poll_info = self.is_poll_status_accordian_present()
            automatic_reply_sms = self.is_automatic_reply_sms_option_present()
            poll_sent_sms = self.is_sent_poll_sms_table()
            return poll_info & automatic_reply_sms & poll_sent_sms
        except:
            return False

    def are_broadcast_poll_accordians_present(self):
        self.select_element(POLL_TAB)
        poll_info = self.is_poll_status_accordian_present()
        automatic_reply_sms = self.is_automatic_reply_sms_option_present()
        return poll_info & automatic_reply_sms

    def is_send_sms_to_more_people_visible(self):
        try:
            return self.driver.find(SEND_SMS_LINK).text == "Send SMS to More People"
        except:
            return False

    def has_DS_received_sms(self, recipent, row, column):
        self.select_element(POLL_TAB)
        self.select_element(POLL_SMS_ACCORDIAN)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_id("poll_sms_table"), True)
        recipient_name = self.driver.find(
            by_xpath(".//*[@id='poll_sms_table']/tbody/tr[%s]/td[%s]" % (row, column))).text
        return recipent in recipient_name

    def deactivate_poll(self):
        self.select_element(POLL_TAB)
        self.select_element(poll_info_accordian)
        self.driver.find(deactivate_link).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, DEACTIVATE_BTN, True)
        self.driver.find_text_box(DEACTIVATE_BTN).click()

    def activate_poll(self):
        self.select_element(POLL_TAB)
        self.select_element(poll_info_accordian)
        self.driver.find(activate_link).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, ACTIVATE_BTN, True)
        self.driver.find_text_box(ACTIVATE_BTN).click()

    def select_send_sms(self):
        self.select_element(POLL_TAB)
        self.click_send_sms_link()

    def click_send_sms_link(self):
        self.select_element(SEND_SMS_LINK)

    def send_sms_to(self, recipient_type, recipient_name):
        self.select_recipient_type(RECIPIENT_DROPDOWN, recipient_type)
        self._configure_given_contacts(recipient_name)
        self.select_element(SEND_BUTTON)
        self.select_element(CANCEL_SMS)

    def send_sms_to_my_poll_recipients(self):
        self.select_recipient_type(RECIPIENT_DROPDOWN, MY_POLL_RECIPIENTS)

    def get_poll_status(self):
        return self.driver.find(by_id("poll_status")).text

    def get_already_active_poll_name(self):
        return self.driver.find(ACTIVE_POLL_NAME).text

    def is_another_poll_active(self, poll_title):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, ACTIVE_POLL_NAME, True)
        return (self.driver.find(POLL_INFORMATION_BOX) is not None) & (self.driver.find(ACTIVE_POLL_NAME).text == poll_title)

    def _configure_given_contacts(self, recipient_name):
        """
        Function to select Group option To whom to send
        return self
        """
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_xpath("//input[@type='checkbox' and @value='%s']" % recipient_name),
                                     True)
        self.driver.find(by_xpath("//input[@type='checkbox' and @value='%s']" % recipient_name)).click()
        return self

    def select_element(self, element):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, element, True)
        self.driver.find(element).click()

    def get_cell_value(self, column, row):
        cell = by_xpath(".//*[@id='datasender_table']/tbody/tr[%s]/td[%s]" % (row+1, column+1))
        self.driver.wait_for_element(UI_TEST_TIMEOUT, cell, True)
        return self.driver.find(cell).text

    def isRecipientAssociated(self, ds_name, row, column):
        return ds_name == self.get_cell_value(column, row)

    def delete_the_poll(self):
        self.select_element(by_css('.delete_project'))
        self.select_element(by_id('confirm_delete_poll'))

from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select

from framework.utils.common_utils import by_css, by_id, generateId, CommonUtilities, by_xpath, by_name
from framework.utils.data_fetcher import fetch_, from_
from pages.createquestionnairepage.create_questionnaire_locator import POLL_SMS_DROPDOWN, \
    POLL_VIA_SMS_RD_BUTTON, SMS_TEXTBOX, CREATE_POLL_BUTTON, POLL_TITLE, DATA_SENDER_TAB, POLL_TAB, DATA_TAB_BTN, \
    POLL_VIA_BROADCAST_RD_BUTTON, active_poll_link, poll_info_accordian, deactivate_link, YES_BUTTON, POLL_STATUS_INFO, \
    AUTOMATIC_REPLY_ACCORDIAN, POLL_SMS_ACCORDIAN, AUTOMATIC_REPLY_SMS_TEXT, AUTOMATIC_REPLY_SECTION, ITALIC_GREY_COMMENT, \
    VIEW_EDIT_SEND, POLL_SMS_TABLE, SEND_MORE_LINK
from pages.page import Page
from tests.projects.questionnairetests.project_questionnaire_data import TYPE, GROUP, OTHERS, CONTACTS_LINKED, DATA_TAB, \
    POLL, POLL_RECIPIENTS
from tests.testsettings import UI_TEST_TIMEOUT

class PollQuestionnairePage(Page):

    def __init__(self, driver):
        Page.__init__(self, driver)
        self.SELECT_FUNC = {
                                GROUP: self._configure_group_recipient,
                                CONTACTS_LINKED: self._configure_linked_contacts,
                            }

    def select_sms_option(self):
        self.driver.find_radio_button(POLL_VIA_SMS_RD_BUTTON).click()

    def select_broadcast_option(self):
        self.driver.find_radio_button(POLL_VIA_BROADCAST_RD_BUTTON).click()

    def enter_sms_text(self):
        self.driver.find_text_box(SMS_TEXTBOX).enter_text("what?")

    def select_receipient(self,receipient, receipient_name):
        recipient_type = fetch_(TYPE, from_(receipient))
        self.select_recipient_type(recipient_type)
        self.SELECT_FUNC[recipient_type](receipient_name)

    def select_recipient_type(self,recipient_type):
        self.driver.find_drop_down(POLL_SMS_DROPDOWN).set_selected(recipient_type)

    def click_create_poll(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT,CREATE_POLL_BUTTON,True)
        self.driver.find(CREATE_POLL_BUTTON).click()

    def is_closed_poll_created(self,poll_title):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, POLL_TITLE, True)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, DATA_SENDER_TAB, True)
        return (self.driver.find(POLL_TITLE).text == poll_title) & self.are_all_tabs_loaded()

    def are_all_tabs_loaded(self):
        data_tab = self.driver.find(DATA_TAB_BTN).text == DATA_TAB
        data_senders_tab = self.driver.find(DATA_SENDER_TAB).text == POLL_RECIPIENTS
        poll_tab = self.driver.find(POLL_TAB).text == POLL
        return data_tab & data_senders_tab & poll_tab

    def is_broadcast_poll_created(self, poll_title):
        data_tab = self.driver.find(DATA_TAB_BTN).text == DATA_TAB
        poll_tab = self.driver.find(POLL_TAB).text == POLL
        return (self.driver.find(POLL_TITLE).text == poll_title) & data_tab & poll_tab

    def is_automatic_reply_sms_option_present(self):
        accordian = self.driver.find(AUTOMATIC_REPLY_ACCORDIAN)
        accordian.click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, AUTOMATIC_REPLY_SECTION, True)
        return self.driver.find(AUTOMATIC_REPLY_SECTION).text.__eq__(AUTOMATIC_REPLY_SMS_TEXT)

    def is_poll_status_accordian_present(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, POLL_STATUS_INFO, True)
        self.driver.find(POLL_STATUS_INFO).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, ITALIC_GREY_COMMENT, True)
        return self.driver.find(ITALIC_GREY_COMMENT).text == VIEW_EDIT_SEND

    def is_sent_poll_sms_table(self):
        self.driver.find(POLL_SMS_ACCORDIAN).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, POLL_SMS_TABLE, True)
        return self.driver.find(POLL_SMS_TABLE) != None

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
        self.driver.find(POLL_TAB).click()
        poll_info = self.is_poll_status_accordian_present()
        automatic_reply_sms = self.is_automatic_reply_sms_option_present()
        return poll_info & automatic_reply_sms

    def is_send_sms_to_more_people_visible(self):
        try:
            return self.driver.find(SEND_MORE_LINK).text == "Send Sms to More People"
        except:
            return False


    # def deactivate_poll(self):
    #     self.driver.find(POLL_TAB).click()
    #     self.driver.find(poll_info_accordian).click()
    #     self.driver.find(deactivate_link).click()
    #     self.driver.wait_for_element(UI_TEST_TIMEOUT, YES_BUTTON, True)
    #     self.driver.find(YES_BUTTON).click()

    def _configure_group_recipient(self, recipient_name):
        """
        Function to select Group option To whom to send
        return self
        """
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_xpath("//input[@type='checkbox' and @value='%s']" % recipient_name),
                                     True)                 # For waiting to load the element
        self.driver.find(by_xpath("//input[@type='checkbox' and @value='%s']" % recipient_name)).click()
        return self


    def _configure_linked_contacts(self, recipient_name):
        """
        Function to select Group option To whom to send
        return self
        """
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_xpath("//input[@type='checkbox' and @value='%s']" % recipient_name),
                                     True)
        self.driver.find(by_xpath("//input[@type='checkbox' and @value='%s']" % recipient_name)).click()
        return self

    def select_tab(self,tab_name):
        self.driver.find(tab_name).click()

    def get_cell_value(self, column, row):
        return self.driver.find(
            by_xpath(".//*[@id='datasender_table']/tbody/tr[%s]/td[%s]" % ((row + 1), column + 1))).text

    def isDataSenderAssociated(self, ds_name, row, column):
        return ds_name == self.get_cell_value(column, row)

from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select

from framework.utils.common_utils import by_css, by_id, generateId, CommonUtilities, by_xpath, by_name
from framework.utils.data_fetcher import fetch_, from_
from pages.createquestionnairepage.create_questionnaire_locator import POLL_SMS_DROPDOWN, \
    POLL_VIA_SMS_RD_BUTTON, SMS_TEXTBOX, CREATE_POLL_BUTTON, POLL_TITLE, DATA_SENDER_TAB, OVERVIEW_TAB, DATA_TAB_BTN
from pages.page import Page
from tests.projects.questionnairetests.project_questionnaire_data import TYPE, GROUP, OTHERS, CONTACTS_LINKED, DATA_TAB, \
    POLL, POLL_RECIPIENTS
from tests.testsettings import UI_TEST_TIMEOUT


class PollQuestionnairePage(Page):

    def __init__(self, driver):
        Page.__init__(self, driver)
        self.SELECT_FUNC = {
                                GROUP: self.configure_group_recipient,
                                CONTACTS_LINKED: self.configure_linked_contacts,
                                # OTHERS: self.configure_other_receipients,
                            }

    def select_sms_option(self):
        self.driver.find_radio_button(POLL_VIA_SMS_RD_BUTTON).click()

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

    def is_poll_created(self,poll_title):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, POLL_TITLE, True)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, DATA_SENDER_TAB ,True)
        return (self.driver.find(POLL_TITLE).text == poll_title) & self.are_all_tabs_loaded()

    def are_all_tabs_loaded(self):
        data_tab = self.driver.find(DATA_TAB_BTN).text == DATA_TAB
        data_senders_tab = self.driver.find(DATA_SENDER_TAB).text == POLL_RECIPIENTS
        overview_tab = self.driver.find(OVERVIEW_TAB).text == POLL
        return data_tab & data_senders_tab & overview_tab


    def configure_group_recipient(self, recipient_name):
        """
        Function to select Group option To whom to send
        return self
        """
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_xpath("//input[@type='checkbox' and @value='%s']" % recipient_name),
                                     True)                 # For waiting to load the element
        self.driver.find(by_xpath("//input[@type='checkbox' and @value='%s']" % recipient_name)).click()
        return self


    def configure_linked_contacts(self, recipient_name):
        """
        Function to select Group option To whom to send
        return self
        """
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_xpath("//input[@type='checkbox' and @value='%s']" % recipient_name),
                                     True)
        self.driver.find(by_xpath("//input[@type='checkbox' and @value='%s']" % recipient_name)).click()
        return self

    # def configure_other_receipients(self, receipient_type, receipient_name):
    #     """
    #     Function to select Group option To whom to send
    #     return self
    #     """
    #     self.driver.find_drop_down(POLL_SMS_DROPDOWN).set_selected(GROUP)
    #     self.driver.wait_for_element(UI_TEST_TIMEOUT, by_xpath("//*[@id='send-sms-section']/div[6]/div[2]/select" % receipient_type),
    #                                  True)
    #     self.driver.wait_for_element(UI_TEST_TIMEOUT, by_xpath("//*[@id='send-sms-section']/div[6]/div[2]/select" % receipient_type)).click()
    #
    #     return self


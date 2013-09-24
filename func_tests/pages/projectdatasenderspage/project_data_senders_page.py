# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from framework.utils.common_utils import by_xpath
from pages.accountpage.account_page import AccountPage
from pages.adddatasenderspage.add_data_senders_page import AddDataSenderPage
from pages.alldatasenderspage.all_data_senders_locator import DATA_SENDER_DEVICES
from pages.projectdatasenderspage.project_data_senders_locator import *
from tests.projects.datasenderstests.registered_datasenders_data import GIVE_WEB_ACCESS
from pages.alldatasenderspage.all_data_senders_page import AllDataSendersPage
from tests.testsettings import UI_TEST_TIMEOUT


class ProjectDataSendersPage(AllDataSendersPage):
    def __init__(self, driver):
        super(ProjectDataSendersPage, self).__init__(driver)

    def navigate_to_add_a_data_sender_page(self):
        """
        Function to navigate to add a data sender page of the website

        Return create project page
         """
        self.driver.find(ADD_A_DATA_SENDER_LINK).click()
        return AddDataSenderPage(self.driver)

    def navigate_to_account_page(self):
        """
        Function to navigate to account page
        """
        self.driver.find(ACCOUNT_LINK).click()
        return AccountPage(self.driver)

    def select_a_data_sender_by_id(self, data_sender_id):
        """
        Function to select a data sender on all data sender page
         """
        self.driver.find(by_xpath(DATA_SENDER_CHECK_BOX_BY_UID_XPATH % data_sender_id)).click()

    def select_a_data_sender_by_mobile_number(self, mobile_number):
        """
        Function to select a data sender on all data sender page
         """
        self.driver.find(by_xpath(DATA_SENDER_CHECK_BOX_BY_MOBILE_XPATH % mobile_number)).click()

    def get_data_sender_email_by_id(self, data_sender_id):
        """
        Function to select a data sender on all data sender page
         """
        email_element = self.driver.find(by_xpath(DATA_SENDER_EMAIL_BY_UID_XPATH % data_sender_id))
        return email_element.text

    def select_web_access_action(self):
        option_to_select = GIVE_WEB_ACCESS
        self.perform_datasender_action(option_to_select)

    def perform_datasender_action(self, action_to_be_performed):
        self.driver.find(ACTION_DROP_DOWN).click()
        option = self.driver.find_visible_element(by_id(action_to_be_performed))
        option.click()

    def give_web_access(self, email_id):
        """
        Function to select give web access action, and then submit the email address
        """
        self.select_web_access_action()
        email_text_box = self.driver.find_text_box(WEB_USER_BLOCK_EMAIL)
        email_text_box.enter_text(email_id)
        self.driver.find(GIVE_ACCESS_LINK).click()

    def get_data_sender_email_by_mobile_number(self, mobile_number):
        """
       Function to select a data sender on all data sender page
        """
        email_element = self.driver.find(by_xpath(DATA_SENDER_EMAIL_BY_MOBILE_NUMBER_XPATH % mobile_number))
        return email_element.text

    def get_error_message(self):
        return self.driver.find(ERROR_MESSAGE_LABEL).text

    def check_sms_device_by_id(self, data_sender_id):
        return self.driver.is_element_present(by_xpath(DATA_SENDER_DEVICES % (data_sender_id, 9)))

    def check_web_device_by_id(self, data_sender_id):
        return self.driver.is_element_present(by_xpath(DATA_SENDER_DEVICES % (data_sender_id, 10)))

    def check_smart_phone_device_by_id(self, data_sender_id):
        return self.driver.is_element_present(by_xpath(DATA_SENDER_DEVICES % (data_sender_id, 11)))

    def open_import_lightbox(self):
        from pages.adddatasenderspage.add_data_senders_locator import OPEN_IMPORT_DIALOG_LINK
        from pages.lightbox.import_datasender_light_box_page import ImportDatasenderLightBox

        self.driver.find(OPEN_IMPORT_DIALOG_LINK).click()
        return ImportDatasenderLightBox(self.driver)

    def click_action_button(self):
        self.driver.find(ACTION_DROP_DOWN).click()

    def is_edit_enabled(self):
        css_class = self.driver.find(EDIT_LI_LOCATOR).get_attribute("class")
        return css_class.find("disabled") < 0

    def is_none_selected_shown(self):
        return self.driver.find(NONE_SELECTED_LOCATOR).is_displayed()

    def actions_menu_shown(self):
        return self.driver.find(ACTION_MENU).is_displayed()

    def click_checkall_checkbox(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, CHECKALL_CB, True)
        self.driver.find(CHECKALL_CB).click()

    def get_number_of_selected_datasenders(self):
        return len([element for element in self.get_inputs_webelement() if element.get_attribute("checked") == "true"])

    def get_all_datasenders_count(self):
        return len(self.get_inputs_webelement())

    def get_inputs_webelement(self):
        return self.driver.find(by_id("associated_data_senders")).find_elements(by="css selector",
                                                                                value="tbody tr td input")

    def is_checkall_checked(self):
        return self.driver.find(CHECKALL_CB).get_attribute("checked") == "true"

    def is_checkall_enabled(self):
        return self.driver.find(CHECKALL_CB).is_enabled()
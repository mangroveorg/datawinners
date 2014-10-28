# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.accountpage.account_page import AccountPage
from pages.adddatasenderspage.add_data_senders_page import AddDataSenderPage
from pages.alldatasenderspage.all_data_senders_locator import DATA_SENDER_DEVICES
from pages.projectdatasenderspage.project_data_senders_locator import *
from tests.projects.datasenderstests.registered_datasenders_data import GIVE_WEB_ACCESS
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT, WAIT

DISASSOCIATE = "disassociate"
class ProjectDataSendersPage(Page):
    def __init__(self, driver):
        super(ProjectDataSendersPage, self).__init__(driver)

    def navigate_to_add_a_data_sender_page(self, wait_for_page_loading=False, lightbox=True):
        """
        Function to navigate to add a data sender page of the website

        Return create project page
         """
        locator = ADD_A_DATA_SENDER_LINK if lightbox else DATASENDER_FORM_TAB_LINK_XPATH
        self.driver.find(locator).click()
        if wait_for_page_loading:
            self.driver.wait_for_element(20, by_id("id_register_button"))
        return AddDataSenderPage(self.driver)

    def navigate_to_account_page(self):
        """
        Function to navigate to account page
        """
        self.driver.find(ACCOUNT_LINK).click()
        return AccountPage(self.driver)

    def select_a_data_sender_by_mobile_number(self, mobile_number):
        """
        Function to select a data sender on all data sender page
         """
        self.driver.find(by_xpath(DATA_SENDER_CHECK_BOX_BY_MOBILE_XPATH % mobile_number)).click()
        return self

    def select_a_data_sender_by_rep_id(self, rep_id):
        """
        Function to select a data sender on all data sender page
         """
        self.driver.find(by_xpath(DATA_SENDER_CHECK_BOX_BY_UID_XPATH % rep_id)).click()
        return self

    def get_data_sender_email_by_id(self, data_sender_id):
        """
        Function to select a data sender on all data sender page
         """
        email_element = self.driver.find(by_xpath(DATA_SENDER_EMAIL_BY_UID_XPATH % data_sender_id))
        return email_element.text

    def select_web_access_action(self):
        option_to_select = GIVE_WEB_ACCESS
        self.perform_datasender_action(option_to_select)

    def disassociate_from_questionnaire(self):
        self.perform_datasender_action(by_css(".remove.from.questionnaire"))
        self.driver.wait_for_element(WAIT, by_css("#datasender_table_wrapper .success-message-box"),True)
        return self

    def perform_datasender_action_to_dissociate(self):
        self.driver.find(ACTION_DROP_DOWN).click()
        option = self.driver.find_visible_element(by_css(".remove.from.questionnaire"))
        option.click()

    def perform_datasender_action(self, locator):
        self.driver.find(ACTION_DROP_DOWN).click()
        option = self.driver.find_visible_element(locator)
        option.click()

        return self

    def navigate_to_analysis_page(self):
        self.driver.find_visible_element(by_id("data_tab")).click()


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

    def is_none_selected_shown(self):
        return self.driver.find(NONE_SELECTED_LOCATOR).is_displayed()

    def select_a_data_sender_by_id(self, data_sender_id):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_xpath(DATA_SENDER_CHECK_BOX_BY_UID_XPATH % data_sender_id),
                                     True)

        self.driver.find(by_xpath(DATA_SENDER_CHECK_BOX_BY_UID_XPATH % data_sender_id)).click()

    def actions_menu_shown(self):
        return self.driver.find(ACTION_MENU).is_displayed()

    def is_edit_disabled(self):
        class_name = self.driver.find(by_xpath(".//a[contains(@class,'edit')]/..")).get_attribute("class")
        return class_name.find('disabled') > 0

    def click_checkall_checkbox(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, CHECKALL_CB, True)
        self.driver.find(CHECKALL_CB).click()

    def get_number_of_selected_datasenders(self):
        return len([element for element in self.get_inputs_webelement() if element.get_attribute("checked") == "true"])

    def get_all_datasenders_count(self):
        return len(self.get_inputs_webelement())

    def get_inputs_webelement(self):
        return self.driver.find(by_id("datasender_table")).find_elements(by="css selector",
                                                                                value="tbody tr td input")

    def is_checkall_checked(self):
        return self.driver.find(CHECKALL_CB).get_attribute("checked") == "true"

    def is_checkall_enabled(self):
        return self.driver.find(CHECKALL_CB).is_enabled()

    def search_with(self, search_text):
        self.driver.find_text_box(by_css("div#datasender_table_filter input")).enter_text(search_text)
        self.wait_for_table_data_to_load()
        return self

    def get_checkbox_selector_for_datasender_row(self, row_number):
        # first row is used to show all rows select message
        return by_xpath(".//*[@id='datasender_table']/tbody/tr[%s]/td[1]/input" % (row_number + 1))


    def wait_for_table_data_to_load(self):
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".dataTables_processing"))
        return self

    def open_setting_popup(self):
        try:
            self.driver.find(by_css("a.change_setting")).click()
        except Exception:
            pass

    def get_setting_value(self):
        return self.driver.find(by_css("[name=ds_setting]:checked")).get_attribute("value")

    def set_setting_value(self, value):
        self.driver.find(by_css("[name=ds_setting][value='%s']" % value)).click()

    def save_setting(self):
        self.driver.find(by_css("#save_ds_setting")).click()

    def set_setting_to_open_datasender(self):
        self.set_setting_value("open")

    def set_setting_to_only_registered_datasender(self):
        self.set_setting_value('restricted')

    def get_setting_description(self):
        description_locator = self.driver.find(by_css("#setting_description"))
        return unicode(self.driver.execute_script("return $(arguments[0]).html()", description_locator))

    def click_cancel_link_on_setting_lightbox(self):
        self.driver.find(by_css("#change_ds_setting a.cancel_link")).click()

    def is_change_setting_option_displayed(self):
        return self.driver.is_element_present(by_css("#setting_description"))
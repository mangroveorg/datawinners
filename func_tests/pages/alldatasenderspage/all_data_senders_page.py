# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.adddatasenderspage.add_data_senders_page import AddDataSenderPage
from pages.alldatasenderspage.all_data_senders_locator import *
from pages.page import Page
from testdata.test_data import DATA_WINNER_ALL_DATA_SENDERS_PAGE
from tests.alldatasenderstests.all_data_sender_data import *
from tests.testsettings import UI_TEST_TIMEOUT


class AllDataSendersPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def navigate_to_add_a_data_sender_page(self):
        """
        Function to navigate to add a data sender page of the website

        Return create project page
         """
        self.driver.find(REGISTER_SENDER_LINK).click()
        return AddDataSenderPage(self.driver)

    def select_a_data_sender_by_mobile(self, data_sender_mobile):
        """
        Function to select a data sender on all data sender page
         """
        self.driver.find(by_xpath(DATA_SENDER_CHECK_BOX_BY_MOBILE_XPATH % data_sender_mobile)).click()

    def select_a_data_sender_by_id(self, data_sender_id):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_xpath(DATA_SENDER_CHECK_BOX_BY_UID_XPATH % data_sender_id), True)
        self.driver.find(by_xpath(DATA_SENDER_CHECK_BOX_BY_UID_XPATH % data_sender_id)).click()

    def select_project(self, project_name):
        self.driver.find(by_xpath(PROJECT_CB_XPATH % project_name)).click()

    def select_projects(self, project_names):
        for project_name in project_names:
            self.select_project(project_name)

    def click_confirm(self, wait=False):
        """
        Function to confirm the association/dissociation with projects on all data sender page
         """
        self.driver.find(CONFIRM_BUTTON).click()
        if wait:
            self.driver.wait_until_modal_dismissed(20)

    def click_cancel(self):
        """
        Function to cancel the association/dissociation with projects on all data sender page
         """
        self.driver.find(CANCEL_LINK).click()

    def click_delete(self, wait=False):
        """
        Function to cancel the association/dissociation with projects on all data sender page
        """
        self.driver.find(DELETE_BUTTON).click()
        if wait:
            self.driver.wait_until_modal_dismissed(7)

    def give_web_access(self):
        """
        Function to give data sender web and smartphone access
         """
        option_to_select = WEB_ACCESS
        self.perform_datasender_action(option_to_select)

    def select_edit_action(self):
        """
        Function to associate data sender with project
         """
        option_to_select = EDIT
        self.perform_datasender_action(option_to_select)

    def perform_datasender_action(self, action_to_be_performed):
        self.driver.find(ACTION_DROP_DOWN).click()
        option = self.driver.find_visible_element(by_id(action_to_be_performed))
        option.click()

    def get_success_message(self):
        """
        Function to fetch the success message from success label
         """
        locator = self.driver.wait_for_element(20, SUCCESS_MESSAGE_LABEL, want_visible=True)
        return locator.text

    def get_delete_success_message(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, DELETE_SUCCESS_MESSAGE, True)
        return self.driver.find(DELETE_SUCCESS_MESSAGE).text

    def get_error_message(self):
        """
        Function to fetch the error message from success label
         """
        return self.driver.find(ERROR_MESSAGE_LABEL).text

    def get_project_names(self, data_sender_id):
        """
        Function to fetch the associated project names from the all data senders page
         """
        return self.driver.find(by_xpath(PROJECT_NAME_LABEL_XPATH % data_sender_id)).text

    def get_uid(self, data_sender_mobile):
        """
        Function to fetch the mobile number from the all data senders page
         """
        return self.driver.find(by_xpath(UID_LABEL_BY_MOBILE_XPATH % data_sender_mobile)).text

    def check_links(self):
        self.driver.is_element_present(DATASENDERS_IMPORT_LINK)
        self.driver.is_element_present(REGISTER_SENDER_LINK)

    def is_web_and_smartphone_device_checkmarks_present(self, data_sender_id):
        checkboxes = self.driver.find_elements_(by_xpath(DATA_SENDER_DEVICES % (data_sender_id)))
        return len(checkboxes) == 3

    def delete_datasender(self, data_sender_id):
        self.select_a_data_sender_by_id(data_sender_id)
        self.perform_datasender_action(DELETE)
        self.click_delete(wait=True)

    # def check_web_device_by_id(self, data_sender_id):
    #     return self.driver.is_element_present(by_xpath(DATA_SENDER_DEVICES % (data_sender_id, 9)))
    #
    # def check_smart_phone_device_by_id(self, data_sender_id):
    #     return self.driver.is_element_present(by_xpath(DATA_SENDER_DEVICES % (data_sender_id, 10)))

    def open_import_lightbox(self):
        from pages.adddatasenderspage.add_data_senders_locator import OPEN_IMPORT_DIALOG_LINK
        from pages.lightbox.import_datasender_light_box_page import ImportDatasenderLightBox

        self.driver.find(OPEN_IMPORT_DIALOG_LINK).click()
        return ImportDatasenderLightBox(self.driver)

    def get_data_sender_email_by_mobile_number(self, data_sender_mobile):
        return self.driver.find(by_xpath(DATA_SENDER_EMAIL_TD_BY_MOBILE_XPATH % data_sender_mobile)).text

    def select_all_datasender_user(self):
        self.driver.find(CHECK_ALL_DS_USER).click()

    def click_checkall_checkbox(self):
        self.driver.find(CHECKALL_DS_CB).click()

    def associate_datasender_to_projects(self, datasender_id, project_names):
        self.select_a_data_sender_by_id(datasender_id)
        self.perform_datasender_action(ASSOCIATE)
        self.select_projects(project_names)
        self.click_confirm(wait=True)

    def dissociate_datasender_from_project(self, datasender_id, project_name):
        self.select_a_data_sender_by_id(datasender_id)
        self.perform_datasender_action(DISSOCIATE)
        self.select_project(project_name)
        self.click_confirm(wait=True)

    def get_datasenders_count(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, ALL_DS_ROWS, True)
        return len(self.driver.find(ALL_DS_ROWS).find_elements(by="tag name", value="tr")[1:])

    def get_checked_datasenders_count(self):
        return len(
            self.driver.find(ALL_DS_ROWS).find_elements(by="css selector", value="tr td:first-child input[checked]"))

    def click_action_button(self):
        self.driver.find(ACTION_DROP_DOWN).click()

    def is_none_selected_shown(self):
        return self.driver.find(NONE_SELECTED_LOCATOR).is_displayed()

    def actions_menu_shown(self):
        return self.driver.find(ACTION_MENU).is_displayed()

    def is_edit_disabled(self):
        css_class = self.driver.find(EDIT_LI_LOCATOR).get_attribute("disabled")
        return bool(css_class)

    def is_checkall_checked(self):
        return self.driver.find(CHECKALL_DS_CB).get_attribute("checked") == "true"

    def edit_datasender(self, uid=None):
        if not uid: return False
        self.select_a_data_sender_by_id(uid)
        self.select_edit_action()
        return AddDataSenderPage(self.driver)

    def is_action_available(self, action_to_be_performed):
        self.driver.find(ACTION_DROP_DOWN).click()
        class_name = self.driver.find(by_xpath(ACTION_LI_BY_ACTION_ID % action_to_be_performed)).get_attribute("class")
        return class_name.find('disabled') < 0

    def is_associate_to_project_action_available(self):
        return self.is_action_available(ASSOCIATE)

    def is_disassociate_to_project_action_available(self):
        return self.is_action_available(DISSOCIATE)

    def select_page_size_of(self, number):
        dropdown = self.driver.find_drop_down(by_css("#datasender_table_length>select"))
        dropdown.click()
        dropdown.set_selected(number)

    def load(self):
        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_id("datasender_table"), True)

    def search_with(self, search_text):
        self.driver.find_text_box(by_css("div#datasender_table_filter > input")).enter_text(search_text)
        self.driver.wait_until_element_is_not_present(20, by_css("loading"))

    def get_empty_table_result(self):
        return self.driver.find_visible_element(by_css("td.dataTables_empty")).text

    def get_checkbox_selector_for_datasender_row(self, row_number):
        return by_xpath(".//*[@id='all_data_senders']/tr[%s]/td[1]/input" % row_number)
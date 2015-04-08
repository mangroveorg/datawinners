from nose.plugins.attrib import attr

from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import random_number
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import login
from tests.allcontactstests.all_contacts_data import VALID_CONTACTS_WITH_WEB_ACCESS


class TestAllContacts(HeadlessRunnerTest):

    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        login(cls.driver)
        cls.global_navigation = GlobalNavigationPage(cls.driver)
        cls.all_contacts_page = cls.global_navigation.navigate_to_all_data_sender_page()
        cls.unique_id = "rep" + random_number(3)


    def _verify_adding_a_group(self):
        self.add_group_page = self.all_contacts_page.go_to_add_group_page()
        group_name = "group_" + random_number(3)
        self.add_group_page.enter_group_name(group_name)
        self.add_group_page.click_on_add_group_button()
        self.assertEquals(self.all_contacts_page.get_success_message(),
                          "Group %s has been added successfully." % group_name)
        return group_name

    def _verify_adding_contact_to_a_group(self, group_name):
        self.all_contacts_page.search_with(self.unique_id)
        self.all_contacts_page.select_a_data_sender_by_id(self.unique_id)
        self.all_contacts_page.perform_datasender_action('add to groups')
        self.add_group_page.add_or_remove_contact_to_group(group_name)
        self.add_group_page.click_on_contact_to_group_button()
        self.assertEquals(self.all_contacts_page.get_flash_message(),
                          "The Contact(s) are added to Group(s) successfully.")

    def _verify_removing_contacts_from_group(self, group_name):
        self.all_contacts_page.select_group_by_name(group_name)
        self.all_contacts_page.search_with(self.unique_id)
        self.assertEquals(self.all_contacts_page.get_cell_value(1, 7), self.unique_id)
        self.all_contacts_page.select_a_data_sender_by_id(self.unique_id)
        self.all_contacts_page.perform_datasender_action('remove from groups')
        self.add_group_page.add_or_remove_contact_to_group(group_name)
        self.add_group_page.click_on_contact_to_group_button()
        self.assertEquals(self.all_contacts_page.get_flash_message(),
                          "The Contact(s) are removed from Group(s) successfully.")
        self.all_contacts_page.select_group_by_name(group_name)
        self.assertEquals(self.all_contacts_page.get_group_table_empty_text(), "Group is empty")

    def _verify_renaming_group(self, group_name):
        self.all_contacts_page.select_group_rename_icon(group_name)
        new_group_name = "group_" + random_number(3)
        self.add_group_page.enter_new_group_name(new_group_name)
        self.add_group_page.click_on_rename_group()
        self.assertEquals(self.all_contacts_page.get_flash_message(), "Group renamed successfully.")
        return new_group_name

    def verify_deleting_a_group(self, new_group_name):
        self.all_contacts_page.click_delete_group_icon(new_group_name)
        self.add_group_page.click_on_confirm_delete_group()
        self.assertEquals(self.all_contacts_page.get_flash_message(), "Group removed successfully.")

    def _creating_a_contact(self):
        self.add_contact_page = self.all_contacts_page.navigate_to_add_a_data_sender_page()
        self.add_contact_page.enter_data_sender_with_mobile_number(VALID_CONTACTS_WITH_WEB_ACCESS,
                                                                   unique_id=self.unique_id)
        self.add_contact_page.get_rep_id_from_success_message(
            self.add_contact_page.get_success_message()) if id is None else id
        self.add_contact_page.close_add_datasender_dialog()
        self.all_contacts_page.search_with(self.unique_id)
        self.assertEquals(self.all_contacts_page.get_cell_value(1, 7), self.unique_id)

    @attr('functional_test')
    def test_group_contact_lifecycle(self):

        self._creating_a_contact()

        group_name = self._verify_adding_a_group()

        self._verify_adding_contact_to_a_group(group_name)

        self._verify_removing_contacts_from_group(group_name)

        new_group_name = self._verify_renaming_group(group_name)

        self.verify_deleting_a_group(new_group_name)






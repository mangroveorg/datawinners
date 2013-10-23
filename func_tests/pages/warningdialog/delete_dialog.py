from framework.utils.common_utils import by_css, by_id
from pages.page import Page


class UserDeleteDialog(Page):

    def __init__(self, driver):
        Page.__init__(self, driver)

    def ok(self):
        self.driver.find(by_css("a.no_button")).click()
        self.driver.wait_until_modal_dismissed(7)

    def get_message(self):
        return self.driver.find(by_css("div#delete_all_ds_are_users_warning_dialog > div.warning_message")).text


class DataSenderDeleteDialog(Page):

    def __init__(self, driver):
        Page.__init__(self, driver)

    def ok(self):
        self.driver.find(by_id("ok_button")).click()
        self.driver.wait_until_modal_dismissed(7)


class DataSenderAndUserDeleteDialog(Page):

    def __init__(self, driver):
        Page.__init__(self, driver)

    def ok(self):
        self.driver.find(by_id("ok_button")).click()
        self.driver.wait_until_modal_dismissed(7)

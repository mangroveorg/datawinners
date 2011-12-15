# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from framework.utils.common_utils import CommonUtilities
from pages.broadcastSMSpage.broadcast_sms_page import BroadcastSmsPage
from pages.page import Page
from pages.reminderpage.all_reminder_locator import *
from pages.reminderpage.reminder_settings_page import ReminderSettingsPage


class AllReminderPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def click_schedule_reminder_tab(self):
        CommonUtilities(self.driver).wait_for_element(3,SCHEDULED_REMINDERS_LINK)
        self.driver.find(SCHEDULED_REMINDERS_LINK).click()

    def click_sent_reminder_tab(self):
        self.driver.find(SENT_REMINDERS_LINK).click()

    def navigate_send_message_tab(self):
        self.driver.find(SEND_MESSAGE_TAB).click()
        return BroadcastSmsPage(self.driver)

    def navigate_reminder_settings_tab(self):
        self.driver.find(REMINDER_SETTINGS_TAB).click()
        return ReminderSettingsPage(self.driver)

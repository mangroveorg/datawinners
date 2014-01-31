# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from framework.utils.data_fetcher import fetch_, from_
from pages.page import Page
from pages.reminderpage.all_reminder_locator import *
from pages.reminderpage.reminder_settings_page import ReminderSettingsPage
from tests.remindertests.reminder_data import FREQUENCY, DAY, TYPE


class AllReminderPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def click_sent_reminder_tab(self):
        self.driver.find(SENT_REMINDERS_LINK).click()

    def click_reminder_settings_tab(self):
        self.driver.find(REMINDER_SETTINGS_TAB).click()
        return ReminderSettingsPage(self.driver)

    def get_warning_message(self):
        return self.driver.find(WARNING_MESSAGE_LABEL).text

    def set_deadline_by_week(self, reminder_settings, deadline):
        reminder_settings.set_frequency(fetch_(FREQUENCY, from_(deadline)))
        reminder_settings.set_week_day(fetch_(DAY, from_(deadline)))
        reminder_settings.set_deadline_type_for_week(fetch_(TYPE, from_(deadline)))
        return reminder_settings

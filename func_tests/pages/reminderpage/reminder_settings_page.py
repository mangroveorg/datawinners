
from pages.page import Page
from pages.reminderpage.reminder_settings_locator import *


class ReminderSettingsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)
        self.enable_reminder = {"before_deadline": self.enable_before_deadline_reminder,
                           "on_deadline": self.enable_on_deadline_reminder,
                           "after_deadline": self.enable_after_deadline_reminder}
        self.disable_reminder = {"before_deadline": self.disable_before_deadline_reminder,
                           "on_deadline": self.disable_on_deadline_reminder,
                           "after_deadline": self.disable_after_deadline_reminder}

    def set_frequency(self, frequency):
        self.driver.find_drop_down(FREQUENCY_PERIOD_DD).set_selected(frequency)

    def set_deadline_type(self, deadline_type):
        self.driver.find_drop_down(DEADLINE_TYPE_DD).set_selected(deadline_type)

    def set_week_day(self, day_name):
        self.driver.find_drop_down(DAYS_OF_WEEK_DD).set_selected_by_text(day_name)

    def set_month_day(self, day_of_the_month):
        self.driver.find_drop_down(DAYS_OF_MONTH_DD).set_selected(day_of_the_month)

    def get_example_text(self):
        self.driver.find(DEADLINE_EXAMPLE_LABEL).text

    def enable_before_deadline_reminder(self):
        checkbox =  self.driver.find(BEFORE_DEADLINE_REMINDER_CB)
        if not checkbox.is_selected():
            checkbox.click()

    def enable_on_deadline_reminder(self):
        checkbox =  self.driver.find(ON_DEADLINE_REMINDER_CB)
        if not checkbox.is_selected():
            checkbox.click()

    def enable_after_deadline_reminder(self):
        checkbox =  self.driver.find(AFTER_DEADLINE_REMINDER_CB)
        if not checkbox.is_selected():
            checkbox.click()

    def send_reminder_only_ds_not_submitted_data(self):
        checkbox =  self.driver.find(ONLY_DATASENDERS_NOT_SUBMITTED_CB)
        if not checkbox.is_selected():
            checkbox.click()

    def disable_before_deadline_reminder(self):
        checkbox =  self.driver.find(BEFORE_DEADLINE_REMINDER_CB)
        if checkbox.is_selected():
            checkbox.click()

    def disable_on_deadline_reminder(self):
        checkbox =  self.driver.find(ON_DEADLINE_REMINDER_CB)
        if checkbox.is_selected():
            checkbox.click()

    def disable_after_deadline_reminder(self):
        checkbox =  self.driver.find(AFTER_DEADLINE_REMINDER_CB)
        if checkbox.is_selected():
            checkbox.click()

    def send_reminder_to_all(self):
        checkbox =  self.driver.find(ONLY_DATASENDERS_NOT_SUBMITTED_CB)
        if checkbox.is_selected():
            checkbox.click()

    def set_message_for_before_deadline_reminder(self, message):
        self.driver.find_text_box(BEFORE_DEADLINE_REMINDER_TB).enter_text(message)

    def get_message_of_before_deadline_reminder(self, message):
        return self.driver.find_text_box(BEFORE_DEADLINE_REMINDER_TB).text

    def set_days_for_before_deadline_reminder(self, message):
        self.driver.find_text_box(NUMBER_OF_DAYS_BEFORE_DEADLINE_TB).enter_text(message)

    def get_days_of_before_deadline_reminder(self, message):
        self.driver.find_text_box(NUMBER_OF_DAYS_BEFORE_DEADLINE_TB).text

    def set_message_for_after_deadline_reminder(self, message):
        self.driver.find_text_box(AFTER_DEADLINE_REMINDER_TB).enter_text(message)

    def get_message_of_after_deadline_reminder(self, message):
        return self.driver.find_text_box(AFTER_DEADLINE_REMINDER_TB).text

    def set_days_for_after_deadline_reminder(self, message):
        self.driver.find_text_box(NUMBER_OF_DAYS_AFTER_DEADLINE_TB).enter_text(message)

    def get_days_of_after_deadline_reminder(self, message):
        return self.driver.find_text_box(NUMBER_OF_DAYS_AFTER_DEADLINE_TB).text

    def set_message_for_on_deadline_reminder(self, message):
        self.driver.find_text_box(AFTER_DEADLINE_REMINDER_TB).enter_text(message)

    def get_message_of_on_deadline_reminder(self, message):
        return self.driver.find_text_box(AFTER_DEADLINE_REMINDER_TB).text

    def save_reminders(self):
        self.driver.find(SAVE_BUTTON).click()

    def get_success_message(self):
        return self.driver.find(SUCCESS_MESSAGE_LABEL).text

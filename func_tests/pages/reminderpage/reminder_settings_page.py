from framework.utils.data_fetcher import from_, fetch_
from pages.AutomaticReplySmsPage.automatic_reply_sms_page import AutomaticReplySmsPage
from pages.page import Page
from pages.reminderpage.all_reminder_locator import WARNING_MESSAGE_LABEL, SENT_REMINDERS_LINK
from pages.reminderpage.reminder_settings_locator import *
from datawinners.project.models import Reminder
from tests.remindertests.reminder_data import *
from tests.testsettings import UI_TEST_TIMEOUT
from framework.exception import CouldNotLocateElementException

REPLY_SMS_LINK = by_css('#reply_sms_tab')

class ReminderSettingsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)
        self.enable_reminder = {BEFORE_DEADLINE: self.enable_before_deadline_reminder,
                           ON_DEADLINE: self.enable_on_deadline_reminder,
                           AFTER_DEADLINE: self.enable_after_deadline_reminder}
        self.disable_reminder_dict = {BEFORE_DEADLINE: self.disable_before_deadline_reminder,
                                 ON_DEADLINE: self.disable_on_deadline_reminder,
                           AFTER_DEADLINE: self.disable_after_deadline_reminder}
    def get_frequency(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, FREQUENCY_PERIOD_DD, True)
        return self.driver.find_drop_down(FREQUENCY_PERIOD_DD).get_selected()

    def set_frequency(self, frequency):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, FREQUENCY_PERIOD_DD, True)
        self.driver.find_drop_down(FREQUENCY_PERIOD_DD).set_selected_by_text(frequency)

    def get_deadline_type_for_week(self):
        return self.driver.find_drop_down(WEEK_DEADLINE_TYPE_DD).get_selected()

    # def set_deadline_type_for_week(self, deadline_type):
    #     self.driver.find_drop_down(WEEK_DEADLINE_TYPE_DD).set_selected_by_text(deadline_type)

    def set_deadline_type_for_month(self, deadline_type):
        self.driver.find_drop_down(MONTH_DEADLINE_TYPE_DD).set_selected_by_text(deadline_type)

    def get_week_day(self):
        return self.driver.find_drop_down(DAYS_OF_WEEK_DD).get_selected()

    def set_week_day(self, day_name):
        self.driver.find_drop_down(DAYS_OF_WEEK_DD).set_selected_by_text(day_name)

    def set_month_day(self, day_of_the_month):
        self.driver.find_drop_down(DAYS_OF_MONTH_DD).set_selected_by_text(day_of_the_month)

    def get_example_text(self):
        return self.driver.find(DEADLINE_EXAMPLE_LABEL).text

    def enable_before_deadline_reminder(self):
        try:
           self.driver.find(SWITCH_ENABLED_BEFORE_DEADLINE)

        except CouldNotLocateElementException:
           self.driver.find(SWITCH_DISABLED_BEFORE_DEADLINE).click()

    def enable_after_deadline_reminder(self):
        try:
           self.driver.find(SWITCH_ENABLED_AFTER_DEADLINE)

        except CouldNotLocateElementException:
           self.driver.find(SWITCH_DISABLED_AFTER_DEADLINE).click()

    def enable_on_deadline_reminder(self):
        try:
           self.driver.find(SWITCH_ENABLED_ON_DEADLINE)

        except CouldNotLocateElementException:
           self.driver.find(SWITCH_DISABLED_ON_DEADLINE).click()

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

    def send_reminder_to_defaulters(self):
        checkbox =  self.driver.find(ONLY_DATASENDERS_NOT_SUBMITTED_CB)
        if not checkbox.is_selected():
            checkbox.click()

    def set_message_for_before_deadline_reminder(self, message):
        textBox = self.driver.find_text_box(BEFORE_DEADLINE_REMINDER_TB).enter_text(message)

    def get_message_of_before_deadline_reminder(self, message):
        return self.driver.find_text_box(BEFORE_DEADLINE_REMINDER_TB).text

    def set_days_for_before_deadline_reminder(self, message):
        self.driver.find_text_box(NUMBER_OF_DAYS_BEFORE_DEADLINE_TB).enter_text(message)

    def get_days_of_before_deadline_reminder(self, message):
        self.driver.find_text_box(NUMBER_OF_DAYS_BEFORE_DEADLINE_TB).text

    def set_message_for_after_deadline_reminder(self, message):
        textBox = self.driver.find_text_box(AFTER_DEADLINE_REMINDER_TB).enter_text(message)

    def get_message_of_after_deadline_reminder(self, message):
        return self.driver.find_text_box(AFTER_DEADLINE_REMINDER_TB).text

    def set_days_for_after_deadline_reminder(self, message):
        self.driver.find_text_box(NUMBER_OF_DAYS_AFTER_DEADLINE_TB).enter_text(message)

    def get_days_of_after_deadline_reminder(self, message):
        return self.driver.find_text_box(NUMBER_OF_DAYS_AFTER_DEADLINE_TB).text

    def set_message_for_on_deadline_reminder(self, message):
        textBox = self.driver.find_text_box(ON_DEADLINE_REMINDER_TB).enter_text(message)

    def get_message_of_on_deadline_reminder(self, message):
        return self.driver.find_text_box(ON_DEADLINE_REMINDER_TB).text

    def save_reminders(self):
        self.driver.find(SAVE_BUTTON).click()

    def navigate_to_automatic_reply_sms_page(self):
        self.driver.find(REPLY_SMS_LINK).click()
        return AutomaticReplySmsPage(self.driver)

    def get_success_message(self):
        return self.driver.find(SUCCESS_MESSAGE_LABEL).text

    def get_reminders_of_project(self, project_id):
        reminder =  Reminder.objects.filter(project_id = project_id)
        reminders = reminder.values("day","message","reminder_mode")
        return reminders

    def get_project_id(self):
        current_url = self.driver.current_url
        values = current_url.split("/")
        return values[values.__len__() - 2]

    def set_reminder(self, reminder_data):
        deadline = fetch_(REMINDER_DEADLINE, from_(reminder_data))
        self.enable_reminder[deadline]()
        if deadline != ON_DEADLINE:
            getattr(self, "set_days_for_%s_reminder" % deadline)(fetch_(DAY, from_(reminder_data)))
        getattr(self, "set_message_for_%s_reminder" % deadline)(fetch_(MESSAGE, from_(reminder_data)))

    def disable_reminder(self, reminder_data):
        deadline = fetch_(REMINDER_DEADLINE, from_(reminder_data))
        self.disable_reminder_dict[deadline]()


    def get_reminder(self, deadline):
        days = "0" if deadline == ON_DEADLINE else getattr(self, "get_days_of_%s_reminder" % deadline)()
        message = getattr(self, "get_message_of_%s_reminder" % deadline)()
        return  {DAY: days, MESSAGE: message, REMINDER_DEADLINE: deadline}

    def set_whom_to_send(self, whom_to_send):
        getattr(self, "send_reminder_to_%s" % whom_to_send)()

    def get_sms_text_length_for_a_reminder_type(self, reminder_type):
        return int(self.driver.find(by_id(SMS_TEXT_COUNTER % reminder_type)).text)

    def set_deadline_by_week(self, deadline):
        self.set_frequency(fetch_(FREQUENCY, from_(deadline)))
        self.set_week_day(fetch_(DAY, from_(deadline)))

    def get_warning_message(self):
        return self.driver.find(WARNING_MESSAGE_LABEL).text

    def click_sent_reminder_tab(self):
        self.driver.find(SENT_REMINDERS_LINK).click()

    @property
    def is_disabled(self):
        elements = self.driver.find_elements_(by_css("input,select"))
        for element in elements:

            if element.is_displayed() and not element.is_enabled():
                return True
        return False

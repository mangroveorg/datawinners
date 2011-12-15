# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time
from framework.utils.global_constant import WAIT_FOR_TITLE
from pages.reviewpage.review_page import ReviewPage
from pages.createreminderpage.create_reminder_locator import *
from pages.page import Page


class CreateReminderPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def save_reminder_successfully(self):
        """
        Function to save the data on set up reminder page

        Return ReviewPage
        """
        self.driver.find(SAVE_CHANGES_BTN).click()
        self.driver.wait_for_page_with_title( WAIT_FOR_TITLE, "Review & Test")
        return ReviewPage(self.driver)

    def click_add_reminder(self):
        self.driver.find(ADD_REMINDER_BTN).click()
        self.driver.wait_for_element(1,by_css(".reminder_content_section"))

    def add_new_reminder_for_days_before(self,days_before):
        self.click_add_reminder()
        self.driver.find(USE_DAYS_BEFORE).click()
        self.driver.find_text_box(SET_DAYS_BEFORE).enter_text(str(days_before))
        self.save_reminders()

    def save_reminders(self):
        self.driver.find(SAVE_REMINDERS_BTN).click()

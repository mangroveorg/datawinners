# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from framework.utils.common_utils import *


# By default every locator should be CSS
# Abbr:
# TB - Text Box
# CB - Check Box
# RB - Radio Button
# BTN - Button
# DD - Drop Down
# LINK - Links
# LABEL - Label


# variable to access locators
LOCATOR = "locator"
BY = "by"

SAVE_CHANGES_BTN = by_css("input#submit-button[value='Next Step: Review and Test']")
ADD_REMINDER_BTN = by_xpath("//button[text()='Add Reminder']")
SAVE_REMINDERS_BTN = by_xpath("//button[text()='Save the reminders']")
USE_DAYS_BEFORE = by_css("div.ui-accordion-content-active input.before_deadline_radio")
SET_DAYS_BEFORE = by_css("div.ui-accordion-content-active input.before_deadline_text")
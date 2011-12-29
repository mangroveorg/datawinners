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

SENT_REMINDERS_LINK = by_css("a#sent_reminders_tab")
REMINDER_SETTINGS_TAB = by_css("a#reminder_settings_tab")
REMINDER_NOT_WORK_FOR_TRIAL_MSG = by_css('div.warning-message-box')

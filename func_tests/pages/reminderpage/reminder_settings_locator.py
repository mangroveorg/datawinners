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
# TA - Text Area

# variable to access locators
LOCATOR = "locator"
BY = "by"

FREQUENCY_PERIOD_DD = by_css("select#id_frequency_period")
DAYS_OF_WEEK_DD = by_css("select#select_deadline")
DAYS_OF_MONTH_DD = by_css("select#id_deadline_month")
WEEK_DEADLINE_TYPE_DD = by_css("select#id_deadline")
MONTH_DEADLINE_TYPE_DD = by_css("select#id_deadline")
DEADLINE_EXAMPLE_LABEL = by_css("#deadline_example")
SWITCH_ENABLED_BEFORE_DEADLINE = by_css('#before_deadline_switch.onoffswitch.onoffswitch-checked')
SWITCH_DISABLED_BEFORE_DEADLINE = by_css('#before_deadline_switch.onoffswitch')
SWITCH_ENABLED_AFTER_DEADLINE = by_css('#after_deadline_switch.onoffswitch.onoffswitch-checked')
SWITCH_DISABLED_AFTER_DEADLINE = by_css('#after_deadline_switch.onoffswitch')
SWITCH_ENABLED_ON_DEADLINE = by_css('#on_deadline_switch.onoffswitch.onoffswitch-checked')
SWITCH_DISABLED_ON_DEADLINE = by_css('#on_deadline_switch.onoffswitch')
BEFORE_DEADLINE_REMINDER_CB = by_css("input#id_should_send_reminders_before_deadline")
NUMBER_OF_DAYS_BEFORE_DEADLINE_TB = by_css("input#id_number_of_days_before_deadline")
BEFORE_DEADLINE_REMINDER_TB = by_css("textarea#id_should_send_reminders_before_deadline")

ON_DEADLINE_REMINDER_CB = by_css("input#id_should_send_reminders_on_deadline")
ON_DEADLINE_REMINDER_TB = by_css("textarea#id_should_send_reminders_on_deadline")

AFTER_DEADLINE_REMINDER_CB = by_css("input#id_should_send_reminders_after_deadline")
NUMBER_OF_DAYS_AFTER_DEADLINE_TB = by_css("input#id_number_of_days_after_deadline")
AFTER_DEADLINE_REMINDER_TB = by_css("textarea#id_should_send_reminders_after_deadline")

ONLY_DATASENDERS_NOT_SUBMITTED_CB = by_css("input#id_whom_to_send_message")
SAVE_BUTTON = by_css("#submit-button")

SUCCESS_MESSAGE_LABEL = by_xpath("//div[@class='success-message-box reminder-success']")
SMS_TEXT_COUNTER = "counter_for_reminder_%s_deadline"

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

DATA_TAB = by_css("a#data_tab")
DATASENDERS_TAB = by_css("a#data_senders_tab")
MESSAGES_AND_REMINDERS_TAB = by_css("a#reminders_tab")
ACTIVATE_PROJECT_LINK = by_css("a.activate_project")
PROJECT_EDIT_LINK = by_css("a#edit_project")
PROJECT_STATUS_LABEL = by_css("span.project_status>span")
TEST_QUESTIONNAIRE_LINK = by_css("a.sms_tester")
SEND_MESSAGE_TAB = by_css("a#send_message_tab")

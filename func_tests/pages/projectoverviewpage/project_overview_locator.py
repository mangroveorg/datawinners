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

DATA_TAB = by_id("data_tab")
DATASENDERS_TAB = by_id("data_senders_tab")
SUBJECTS_TAB = by_id("subjects_tab")
MESSAGES_AND_REMINDERS_TAB = by_id("reminders_tab")
ACTIVATE_PROJECT_LINK = by_css("a.activate_project")
PROJECT_EDIT_LINK = by_id("edit_project")
PROJECT_STATUS_LABEL = by_css("span.project_status>span")
TEST_QUESTIONNAIRE_LINK = by_css("a.sms_tester")
SEND_MESSAGE_TAB = by_id("send_message_tab")
QUESTIONNAIRE_TAB = by_id("questionnaire_tab")
PROJECT_TITLE_LOCATOR = by_css("h2.project_title")
QUESTION_CODE_CONTAINER = by_css(".questionnaire-code")
REVIEW_AND_TEST_TAB = by_id("review_tab")
WEB_QUESTIONNAIRE_PAGE = by_css(".web_questionnaire")

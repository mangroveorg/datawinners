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

# List of all the locators related to login page
ADD_NEW_SUBJECT_TYPE_LINK = by_xpath("//div[@id='subject_create_type_link']/a[@id='add_new_subject_type']|//h3/a[@id='add_new_subject_type']")
NEW_SUBJECT_TB = by_css("input#id_entity_type_text")
ADD_BTN = by_css("input#add_type")

ERROR_MESSAGE_LABEL = by_css("div#type_message.message-box")


CHECK_ALL_SUBJECT_TYPE_LOCATOR = by_css("#check_all_type")
ALL_SUBJECT_TYPE_ACTION_SELECT = by_css(".action")
CONFIRM_DELETE_BUTTON = by_css("#delete_subject_type_warning_dialog a.yes_button")
CANCEL_DELETE_BUTTON = by_css("#delete_subject_type_warning_dialog a.no_button")
ACTION_MENU = by_id("action")
MESSAGES_CONTAINER = by_css("span.message-span")
CHECK_ONE_SUBJECT_TYPE = by_css(".all_subject_type_table tbody tr:nth-child(3) td input")
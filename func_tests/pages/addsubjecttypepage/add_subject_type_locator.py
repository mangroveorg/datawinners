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
ADD_NEW_SUBJECT_TYPE_LINK = by_css("a#add_new_subject_type")
NEW_SUBJECT_TB = by_css("div[class~='ui-accordion-content-active']>input#id_entity_type_text")
ADD_BTN = by_css("div[class~='ui-accordion-content-active']>input#add_type")

ERROR_MESSAGE_LABEL = by_css("div[class~='ui-accordion-content-active']>div#type_message.message-box")

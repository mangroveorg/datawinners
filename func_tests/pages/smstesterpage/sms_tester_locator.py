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

FROM_TB = by_css("input#id_from_number")
TO_TB = by_css("input#id_to_number")
SMS_TA = by_css("textarea#id_message")

SEND_SMS_BTN = by_css("input[value='Send SMS']")

ERROR_MESSAGE_LABEL = by_css("div[class~='error']")
FLASH_MSG_LABEL = by_css("div#flash-message")

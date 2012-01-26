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


# variable to access locator
LOCATOR = "locator"
BY = "by"

ENTITY_TYPE_DD = by_css("select#id_entity_type")
DROP_DOWN_OPTION_CSS = "select#id_entity_type>option[value='%s']"
SHORT_NAME_ENABLED_TB = by_css("input#short_name:enabled")
SHORT_NAME_DISABLED_TB = by_css("input#short_name:disabled")
AUTO_GENERATE_CB = by_css("input#generate_id")
NAME_TB = by_css("input#entity_name")
LOCATION_TB = by_css("input#id_l")
GEO_CODE_TB = by_css("input#id_g")
DESCRIPTION_TB = by_css("textarea#description")
MOBILE_NUMBER_TB = by_css("input#id_m")

FNAME_TB = by_css("input#id_f")
LNAME_TB = by_css("input#id_n")
UNIQUE_ID_TB = by_css("input#id_s")
SUBMIT_BTN = by_css("input[value='Submit']")

ADD_BTN = by_css("input#register_entity")
ERROR_MESSAGE_LABEL = by_css("ul.errorlist>li") #by_xpath("//div[@class='error_message message-box'] | //label[@class='error']/../../..")
ERROR_MESSAGE_BOX = by_css("div.message-box")
FLASH_MESSAGE_LABEL = by_xpath("//div[@class='success-message-box' and not(contains(@id,'none'))]")

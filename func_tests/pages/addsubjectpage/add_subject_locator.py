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
AUTO_GENERATE_CB = by_css("input#autogen")
NAME_TB = by_css("input#entity_name")
LOCATION_TB = by_css("input#id_location")
GEO_CODE_TB = by_css("input#geo_code")
DESCRIPTION_TB = by_css("textarea#description")
MOBILE_NUMBER_TB = by_css("input#mobile_number")

ADD_BTN = by_css("input#register_entity")
ERROR_MESSAGE_LABEL = by_xpath("//div[@class='error_message message-box'] | //label[@class='error']/../../..")
FLASH_MESSAGE_LABEL = by_xpath("//div[@class='success-message-box' and not(contains(@id,'none'))]")


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

LOCATOR = "locator"
BY = "by"

#Registration Page Locator
ORGANIZATION_NAME_TB = by_css("input[name=name]")
ORGANIZATION_SECTOR_DD = by_css("select[name='sector']")
ORGANIZATION_ADDRESS_TB = by_css("input[name=address]")
ORGANIZATION_CITY_TB = by_css("input[name=city]")
ORGANIZATION_STATE_TB = by_css("input[name=state]")
ORGANIZATION_COUNTRY_TB = by_css("input[name=country]")
ORGANIZATION_ZIPCODE_TB = by_css("input[name=zipcode]")
ORGANIZATION_OFFICE_PHONE_TB = by_css("input[name=office_phone]")
ORGANIZATION_WEBSITE_TB = by_css("input[name=website]")
ORGANIZATION_TITLE_TB = by_css("input[name=title]")
ORGANIZATION_FIRST_NAME_TB = by_css("input[name=first_name]")
ORGANIZATION_LAST_NAME_TB = by_css("input[name=last_name]")
ADMIN_OFFICE_NUMBER_TB = by_css("input#id_office_phone")
ADMIN_MOBILE_NUMBER_TB = by_css("input#id_mobile_phone")
SKYPE_ID_TB = by_css("input#id_skype")
ORGANIZATION_UPGRADE_BTN = by_css("input[value='Upgrade']")
AGREE_TERMS_CB = by_css("input#agree-terms")
ABOUT_DATAWINNERS_BOX = by_xpath('//div[@class="grid_7 right_hand_section alpha omega about_datawinners"')
ERROR_MESSAGE_LABEL = by_xpath("//ul[@class='errorlist']/..")
ORGANIZATION_SECTOR_DROP_DOWN_LIST = by_css("select#sector")

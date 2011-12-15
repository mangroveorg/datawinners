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
ORGANIZATION_NAME_TB = by_css("input[name=organization_name]")
ORGANIZATION_SECTOR_DD = by_css("select[name='organization_sector']")
ORGANIZATION_ADDRESS_TB = by_css("input[name=organization_address]")
ORGANIZATION_CITY_TB = by_css("input[name=organization_city]")
ORGANIZATION_STATE_TB = by_css("input[name=organization_state]")
ORGANIZATION_COUNTRY_TB = by_css("input[name=organization_country]")
ORGANIZATION_ZIPCODE_TB = by_css("input[name=organization_zipcode]")
ORGANIZATION_OFFICE_PHONE_TB = by_css("input[name=organization_office_phone]")
ORGANIZATION_WEBSITE_TB = by_css("input[name=organization_website]")
ORGANIZATION_TITLE_TB = by_css("input[name=title]")
ORGANIZATION_FIRST_NAME_TB = by_css("input[name=first_name]")
ORGANIZATION_LAST_NAME_TB = by_css("input[name=last_name]")
ORGANIZATION_EMAIL_TB = by_css("input[name=email]")
ADMIN_OFFICE_NUMBER_TB = by_css("input#id_office_phone")
ADMIN_MOBILE_NUMBER_TB = by_css("input#id_mobile_phone")
SKYPE_ID_TB = by_css("input#id_skype")
ORGANIZATION_PASSWORD_TB = by_css("input[name=password1]")
ORGANIZATION_CONFIRM_PASSWORD_TB = by_css("input[name=password2]")
ORGANIZATION_REGISTER_BTN = by_css("input[value='Sign Up']")
AGREE_TERMS_CB = by_css("input#agree-terms")

ERROR_MESSAGE_LABEL = by_xpath("//ul[@class='errorlist']/..")

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

SMS_TA = by_xpath("//div[@role='dialog' and contains(@style,'block')]/..//textarea[@id='id_message']")

SEND_SMS_BTN = by_xpath("//div[@role='dialog' and contains(@style,'block')]/..//input[@id='send_sms']")
CLEAR_BTN = by_xpath("//div[@role='dialog' and contains(@style,'block')]/..//input[@id='clear_sms']")
UPGRADE_INSTRUCTION_BY_CSS = by_css("div.sms_tester_form > div.warning-message-box p")

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
# TR - Table Row

# variable to access locators
LOCATOR = "locator"
BY = "by"

SUBMISSION_LOG_TR = by_xpath("//div[@id='sms_results']//../table/tbody/tr[2]")
SUBMISSION_LOG_TR_XPATH = "//div[@id='sms_results']//../table/tbody/tr/td[contains(text(),\"%s\")]/.."
SUBMISSION_LOG_FAILURE_MSG_XPATH = "/td[5]/span"
ACTIVE_TAB_LOCATOR = by_css("ul.secondary_tab li.active")
ACTION_SELECT_CSS_LOCATOR = by_css("#action")
CHECKALL_CB_CSS_LOCATOR = by_css("#master_checkbox")
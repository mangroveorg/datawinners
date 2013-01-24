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

SUBMISSION_LOG_TR = by_xpath("//div[@id='submission_logs']//../table/tbody/tr[2]")
SUBMISSION_LOG_TR_XPATH = "//div[@id='submission_logs']//../table/tbody/tr/td[contains(text(),\"%s\")]/.."
SUBMISSION_LOG_FAILURE_MSG_XPATH = "/td[5]/span"
ACTIVE_TAB_LOCATOR = by_css("ul.secondary_tab li.active")
ACTION_SELECT_CSS_LOCATOR = by_css(".table_information .action")
DELETE_BUTTON = by_css("#action_menu .delete")
CHECKALL_CB_CSS_LOCATOR = by_id("master_checkbox")
SHOWN_RECORDS_COUNT_CSS_LOCATOR = by_css(".dataTables_info span:first-child")
XPATH_TO_CELL = "//div[@id='submission_logs']//../table/tbody/tr[%s]/td[%s]"
HEADER_CELL_CSS_LOCATOR = "#submission_logs table>thead>tr>th:nth-child(%s)"
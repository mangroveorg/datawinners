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

ANALYSIS_LINK = by_css("ul.secondary_tab>li>a:contains('Analysis')")
ALL_DATA_RECORDS_LINK = by_xpath("//ul[@class='secondary_tab']/li/a[text()='All Data Records']")
LOADING_GIF = by_css("#h1 .loading")

QUESTION_LABEL_CSS = "table#data_analysis>thead>tr>th:nth-child(%s)"
DATA_ROW_BY_ENTITY_ID_XPATH = "//table[@id='data_analysis']/tbody/tr/td[text()='%s']"
DATA_ROWS = by_css("table#data_analysis>tbody>tr")
QUESTION_LABELS = by_css("table#data_analysis>thead>tr>th")
DATE_RANGE_PICKER_TB = by_css("input#dateRangePicker")
CURRENT_MONTH_LABEL = by_xpath("//div[contains(@class,'ui-daterangepicker') and contains(@style,'block')]/ul/li/a[text()='Current month']")
LAST_MONTH_LABEL = by_xpath("//div[contains(@class,'ui-daterangepicker') and contains(@style,'block')]/ul/li/a[text()='Last Month']")
YEAR_TO_DATE_LABEL = by_xpath("//div[contains(@class,'ui-daterangepicker') and contains(@style,'block')]/ul/li/a[text()='Year to date']")
FILTER_BUTTON = by_css("input#time_submit")
NEXT_BUTTON = by_css("span#data_analysis_next[class='next paginate_button']")
NEXT_BUTTON_DISABLED = by_css("span#data_analysis_next[class='next paginate_button paginate_button_disabled']")
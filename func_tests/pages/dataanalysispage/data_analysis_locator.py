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
ALL_DATA_RECORDS_LINK = by_xpath("//ul[@class='secondary_tab']/li/a[text()='Submission Log']")
LOADING_GIF = by_css("#h1 .loading")

PAGE_SIZE_SELECT = by_name("data_analysis_length")
QUESTION_LABEL_CSS = "table#data_analysis>thead>tr>th:nth-child(%s)"
DATA_ROW_BY_ENTITY_ID_XPATH = "//table[@id='data_analysis']/tbody/tr/td[text()='%s']"
DATA_ROWS = by_css("table#data_analysis>tbody>tr")
QUESTION_LABELS = by_css("table#data_analysis>thead>tr>th")
REPORTING_PERIOD_PICKER_TB = by_id("reportingPeriodPicker")
SUBMISSION_DATE_PICKER_TB = by_id("submissionDatePicker")
KEYWORD_TB = by_id("keyword")
CLEAR_DROPDOWN_LINK =  by_css(".ui-dropdownchecklist-close>a")
DROPDOWN_CONTROL = by_css(".ui-dropdownchecklist-selector-wrapper")
DROPDOWN_WRAPPER = by_css('.ui-dropdownchecklist-dropcontainer-wrapper')
TOTAL_RECORD_LABEL = by_id("total_count")
DATE_PICKER_WRAPPER = by_css(".ui-daterangepicker")
CURRENT_MONTH_LABEL = by_xpath("//div[contains(@class,'ui-daterangepicker') and contains(@style,'block')]/ul/li/a[text()='Current month']")
LAST_MONTH_LABEL = by_xpath("//div[contains(@class,'ui-daterangepicker') and contains(@style,'block')]/ul/li/a[text()='Last Month']")
YEAR_TO_DATE_LABEL = by_xpath("//div[contains(@class,'ui-daterangepicker') and contains(@style,'block')]/ul/li/a[text()='Year to date']")
DAILY_DATE_RANGE_LABEL = by_xpath("//div[contains(@class,'ui-daterangepicker') and contains(@style,'block')]/ul/li/a[text()='Choose Date(s)']")
MONTHLY_DATE_RANGE_LABEL = by_xpath("//div[contains(@class,'ui-daterangepicker') and contains(@style,'block')]/ul/li/a[text()='Choose Month(s)']")
FILTER_BUTTON = by_id("go")
NEXT_BUTTON = by_id("data_analysis_next")
NEXT_BUTTON_DISABLED = by_css("#data_analysis_next[class='next paginate_button paginate_button_disabled']")
CHART_VIEW_LINK = by_css(".chart")
CHART_ELEMENT = by_css("#chart-0")
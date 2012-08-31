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

ACTIVATE_BTN = by_xpath("//div[@role='dialog' and contains(@style,'block')]/div/a[@id='confirm']")
CONFIRMATION_BTN = by_xpath("//div[@role='dialog' and contains(@style,'block')]/div/a[@id='continue']")
CANCEL_LINK = by_xpath("//div[@role='dialog' and contains(@style,'block')]/div/a[@class='cancel_link']")
CLOSE_BTN = by_xpath(
    "//div[@role='dialog' and contains(@style,'block')]/div/a/span[@class='ui-icon ui-icon-closethick']")
MESSAGE_LABEL = by_xpath("//div[@role='dialog' and contains(@style,'block')]/div/p[@class='warning_message']")
TITLE_LABEL = by_xpath("//div[@role='dialog' and contains(@style,'block')]/div/span[@class='ui-dialog-title']")
CHANGE_DATE_FORMAT_CONTINUE_BTN = by_xpath("//div[@role='dialog' and contains(@style,'block')]/div/a[@id='change_date_format_continue']")
DOWNLOAD_TEMPLATE_LINK = by_css(".import_link")

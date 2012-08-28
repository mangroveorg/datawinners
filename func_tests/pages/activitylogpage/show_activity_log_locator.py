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

FIND_DATA_BY_ROW_AND_COLUMN_NUMBER = "#users_list #log_data tbody tr:nth-child(%s) td:nth-child(%s)"
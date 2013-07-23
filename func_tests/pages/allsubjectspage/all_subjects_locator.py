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

ADD_A_SUBJECT_LINK = by_css("a[class~='add_subject_link']")
ADD_SUBJECT_TYPE_LINK = by_css("#subject_create_type_link > a")
NEW_SUBJECT_TYPE_TB = by_css("#id_entity_type_text")
ADD_SUBJECT_TYPE_SUBMIT_BUTTON = by_css("#add_type")
CONTINUE_EDITING_BUTTON = by_css("#edit_warning > div > a")
SUBJECT_TYPE_LINK = '//a[@class="header" and text()="%s"]'
SUBJECTS_INFO = '//div[@id="all_subjects"]/div/span[@class="header" and text()="%s"]/following-sibling::span[1]'
CHECKALL_CB = 'table#%s-table thead tr th:first-child input'
SUBJECT_TABLE_TBODY = 'table#%s-table tbody'
ALL_SUBJECT_TYPES_CONTAINER = by_css("div#all_subjects")
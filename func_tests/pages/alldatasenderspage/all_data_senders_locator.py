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

ADD_A_DATA_SENDER_LINK = by_css("a[class~='add_subject_link']")
DATA_SENDER_CHECK_BOX_BY_MOBILE_XPATH = "//tr/td[6][text()='%s']/../td[1]/input"
DATA_SENDER_EMAIL_TD_BY_MOBILE_XPATH = "//tr/td[6][text()='%s']/../td[7]"
DATA_SENDER_CHECK_BOX_BY_UID_XPATH = "//input[@id='%s']"
PROJECT_CB_XPATH = "//div[contains(@class,'ui-dialog') and contains(@style, 'block')]/div/ul[@id='all_projects']/li[text()='%s']/input"
ACTION_DROP_DOWN = by_css(".action")
PROJECT_NAME_LABEL_XPATH = "//tr/td/input[@id='%s']/../../td[11]"
UID_LABEL_BY_MOBILE_XPATH = "//tr/td[7][text()='%s']/../td[2]"
DATA_SENDER_DEVICES = "//tr/td/input[@id='%s']/../../td[%d]/img"
WEB_USER_BLOCK_EMAIL = by_css("div#web_user_block input.ds-email")
GIVE_ACCESS_LINK = by_id('web_user_button')

CANCEL_LINK = by_xpath("//div[contains(@class,'ui-dialog') and contains(@style, 'block')]/div/a[@id='cancel_link']")
CONFIRM_BUTTON = by_xpath("//div[contains(@class,'ui-dialog') and contains(@style, 'block')]/div/a[text()='Confirm']")
DELETE_BUTTON = by_css("a#ok_button")

ERROR_MESSAGE_LABEL = by_css("div#error.message-box")
SUCCESS_MESSAGE_LABEL = by_xpath("//div[@class='success-message-box' and not(contains(@id,'none'))]")
DELETE_SUCCESS_MESSAGE = by_xpath("//ul[@class='messages']/li")
IMPORT_LINK = by_css("a#import-datasenders")
CHECK_ALL_DS_USER = by_css("input.is_user")
CHECKALL_DS_CB = by_id("checkall-datasenders")
ALL_DS_ROWS = by_css("#all_data_senders")
NONE_SELECTED_LOCATOR = by_id("none-selected")
ACTION_MENU = by_id("action")
EDIT_LI_LOCATOR = by_xpath("//a[@id='edit']/parent::li")
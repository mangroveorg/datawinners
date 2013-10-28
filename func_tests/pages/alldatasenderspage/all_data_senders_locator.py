from framework.utils.common_utils import by_css, by_id, by_xpath

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

REGISTER_SENDER_LINK = by_css("a[class~='add_subject_link']")
DATA_SENDER_CHECK_BOX_BY_MOBILE_XPATH = "//tr/td[6][text()='%s']/../td[1]/input"
DATA_SENDER_EMAIL_TD_BY_MOBILE_XPATH = "//tr/td[6][text()='%s']/../td[7]"
DATA_SENDER_CHECK_BOX_BY_UID_XPATH = "//input[@value='%s']"
PROJECT_CB_XPATH = "//div[contains(@class,'ui-dialog') and contains(@style, 'block')]/div/ul[@id='all_projects']/li[text()='%s']/input"
ACTION_DROP_DOWN = by_css(".btn.dropdown-toggle.action")
PROJECT_NAME_LABEL_XPATH = "//input[@value='%s']/../../td[9]"
UID_LABEL_BY_MOBILE_XPATH = "//tr/td[7][text()='%s']/../td[2]"
DATA_SENDER_DEVICES = "//input[@value='%s']/../../td[8]/img"
WEB_USER_BLOCK_EMAIL = by_css("div#web_user_block input.ds-email")
GIVE_ACCESS_LINK = by_id('web_user_button')

CANCEL_LINK = by_xpath("//div[contains(@class,'ui-dialog') and contains(@style, 'block')]/div/a[@id='cancel_link']")
CONFIRM_BUTTON = by_xpath("//div[contains(@class,'ui-dialog') and contains(@style, 'block')]/div/a[text()='Confirm']")
DELETE_BUTTON = by_css("a#ok_button")

ERROR_MESSAGE_LABEL = by_css("div#error.message-box")
SUCCESS_MESSAGE_LABEL = by_xpath("//div[@class='success-message-box' and not(contains(@id,'none'))]")
DELETE_SUCCESS_MESSAGE = by_css("div.success-message-box")
DATASENDERS_IMPORT_LINK = by_id("a#import-datasenders")
CHECK_ALL_DS_USER = by_css("input.is_user")
CHECKALL_DS_CB = by_xpath(".//*[@id='datasender_table']/thead/tr/th[1]/input")
ALL_DS_ROWS = by_css("#datasender_table")
NONE_SELECTED_LOCATOR = by_xpath(".//li[contains(@class,'none-selected')]")
ACTION_MENU = by_xpath(".//ul[contains(@class,'dropdown-menu')]")

ACTION_LI_LOCATOR = ".//a[contains(@class,'%s')]/.."

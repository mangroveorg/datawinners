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

QUESTIONNAIRE_CODE_TB = by_css("input#questionnaire-code")
QUESTION_TB = by_xpath("//input[@id='question_title']")
CODE_TB = by_css("input#code")

ANSWER_TYPE_DROPDOWN = by_css(".dropdown select")
POLL_SMS_DROPDOWN = by_css(".sms_dropdown select")
POLL_VIA_SMS_RD_BUTTON = by_id('poll_via_sms')
POLL_VIA_BROADCAST_RD_BUTTON = by_id('poll_via_broadcast')
SMS_TEXTBOX = by_id('sms-text')
POLL_TITLE = by_css(".project_title")
CREATE_POLL_BUTTON = by_css('.create_poll_button')
DATA_TAB_BTN = by_id("data_tab")
DATA_SENDER_TAB = by_id("data_senders_tab")
POLL_TAB = by_id("poll_tab")
WORD_OR_PHRASE_RB = by_css("input[value='text']")
POLL_STATUS_INFO = by_id("poll_status_info")
AUTOMATIC_REPLY_ACCORDIAN = by_id("automatic_reply")
AUTOMATIC_REPLY_SECTION = by_id("automatic_reply_section")
POLL_SMS_ACCORDIAN = by_id("poll_sms_info")
ITALIC_GREY_COMMENT = by_css(".italic_grey")
VIEW_EDIT_SEND = "View, edit & send your Survey."
POLL_SMS_TABLE = by_id("poll_sms_table")
SEND_SMS_LINK = by_id("send_sms")
SEND_BUTTON = by_id("send_button")
CANCEL_SMS = by_id("cancel-sms")
PROJECT_LANGUAGE = by_id("project_language")
ON_SWITCH = by_css(".onoffswitch-checked")
ON_OFF_SWITCH = by_css(".onoffswitch-label")
SAVE_LANG_BTN = by_id("save_lang")
SUCCESS_MSG_BOX = by_css(".success-message-box")
RECIPIENT_DROPDOWN = by_id("recipient-dropdown")
AUTOMATIC_REPLY_SMS_TEXT = 'Send Automatic SMS Replies for My Poll'
WORD_OR_PHRASE = 'text'
LANGUAGE_TEXT = by_css(".title_set_SMS")
NUMBER_OPTION = 'integer'
DATE_OPTION = 'date'
LIST_OF_CHOICES_OPTION = 'choice'
GPS_COORDINATES = 'geocode'
UNIQUE_ID_OPTION = 'unique_id'
GROUP_OPTION = 'group'
LINKED_CONTACTS = 'linked'
OTHERS = 'others'
ACTIVE_POLL_NAME = by_id('active_poll_name')
poll_info_accordian = by_id('poll_status_info')
deactivate_link = by_id('deactivate_link')
activate_link = by_id('activate_link')
POLL_INFORMATION_BOX = by_css(".information_box")
DEACTIVATE_BTN = by_xpath(".//*[contains(concat(' ', @class, ' '), ' ui-dialog-content')]/div/button[@id='deactivate_button']")

ACTIVATE_BTN = by_xpath(".//*[contains(concat(' ', @class, ' '), ' ui-dialog-content')]/div/button[@id='activate_button']")

FIRST_CREATED_POLL = by_xpath(".//*[@id='container_content']/div[2]/div[2]/div/table/tbody/tr[22]/td[1]/a")
NEW_UNIQUE_ID_TEXT = by_css('.newUniqueIdName')
UNIQUE_ID_CHOICE_BOX = by_css('.uniqueIdType')
UNIQUE_ID_COMBO_BOX = by_css('.uniqueIdTypeContents')
NEW_UNIQUE_ID_ADD_BUTTON = by_css('.newUniqueIdBox .button_blue')
UNIQUE_ID_TYPE_LIST = by_css('.uniqueIdList li')
NO_CHARACTER_LIMIT_RB = by_xpath(
    "//*/input[@value='length_unlimited']")
CHARACTER_LIMIT_RB = by_xpath(
    "//*/input[@value='length_limited']")
WORD_OR_PHRASE_MAX_LENGTH_TB = by_xpath(
    "//li[not(contains(@style,'none')) and contains(@data-bind,'showAddTextLength')]//../input[@id='max_length' and not(contains(@style,'none'))]")
NUMBER_RB = by_css("input[value='integer']")
NUMBER_MAX_LENGTH_TB = by_xpath(
    "//li[not(contains(@style,'none')) and contains(@data-bind,'showAddRange')]/div/div/input[@id='range_max']")
NUMBER_MIN_LENGTH_TB = by_xpath(
    "//li[not(contains(@style,'none')) and contains(@data-bind,'showAddRange')]/div/div/input[@id='range_min']")

DATE_RB = by_css("input[value='date']")
MONTH_YEAR_RB = by_xpath("//input[@value='mm.yyyy']")
DATE_MONTH_YEAR_RB = by_xpath("//input[@value='dd.mm.yyyy']")
MONTH_DATE_YEAR_RB = by_xpath("//input[@value='mm.dd.yyyy']")

LIST_OF_CHOICE_RB = by_css("input[value='choice']")
CHOICE_XPATH_LOCATOR = "//li[not(contains(@style,'none')) and contains(@data-bind,'showAddChoice')]/div/ol/li"
CHOICE_TB_XPATH_LOCATOR = "/input"
CHOICE_S_XPATH_LOCATOR = "/span"
CHOICE_DL_XPATH_LOCATOR = "/a"
CHOICE_DELETE_LINK_XPATH_LOCATOR = "/p/a[text()='delete']"
ADD_CHOICE_LINK = by_xpath("//li[not(contains(@style,'none')) and contains(@data-bind,'showAddChoice')]/div/a")
ONLY_ONE_ANSWER_RB = by_css("input[value='select1']")
MULTIPLE_ANSWER_RB = by_css("input[value='select']")

GEO_RB = by_css("input[value='geocode']")
CHARACTER_COUNT = by_css("span#char-count")
BACK_LINK = by_css("a#back_to_project")

PREVIOUS_STEP_LINK = by_xpath("//a[@id='subjects_link' and text()='Subjects']")

# Locators for Question List section of the page
DEFAULT_QUESTION_LINK = by_xpath(
    "//div[@class='question_list']/ol/li[1]/a[1]")
QUESTION_LINK_CSS_LOCATOR_PART1 = "div.question_list>ol>li"  # index number to identify question
QUESTION_LINK_CSS_LOCATOR_PART2 = ">a"  # Add text to locate specific question
LAST_QUESTION_LINK_LOCATOR = by_css(".question_list li:last-child>a")
QUESTION_DELETE_LINK_CSS_LOCATOR_PART1 = "div.question_list>ol>li"  # Add text or index number to identify question
QUESTION_DELETE_LINK_CSS_LOCATOR_PART2 = ">div.delete>a"
ADD_A_QUESTION_LINK = by_css("div.add_question>a")
SAVE_CHANGES_BTN = by_css("input#submit-button")

SUCCESS_MESSAGE_LABEL = by_xpath(
    "//div[@id='message-label']/label[@class='success_message' and not(contains(@style,'none'))]")
PERIOD_QUESTION_TIP_CSS_LOCATOR = "#periode_green_message"
QUESTION_TYPE_CSS_LOCATOR = "[name=type][value='%s']"
CURRENT_QUESTION_TYPE_LOCATOR = by_css("input[name='type']:checked")

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

WELCOME_MESSAGE_LABEL = by_css("span.welcome")
CREATE_PROJECT_LINK = by_css("a#create_project_link")
LIGHTBOX_LOCATOR = by_css("div.ui-dialog")
TAKE_A_TOUR_LOCATOR = by_xpath("//a[contains(text(),'Take a Tour')]")
CLOSE_LIGHTBOX_LOCATOR = by_css("a.ui-dialog-titlebar-close")
GET_STARTED_LOCATOR = by_xpath("//a[contains(text(),'Create Your')]")

HELP_ELEMENT_WELCOME = by_css("#welcome_area h4")
CLOSE_HELP_ELEMENT_BUTTON = by_css("#welcome_area a.close_help_element")
HELP_DIALOG = by_css("#help_message_content")
CLOSE_HELP_DIALOG = by_css("#help_message_dialog_close")
PROJECTS_LIST_LOCATOR = by_css("#projects .project_header a")
SEND_A_MSG_LINK_LOCATOR = by_id('send_sms')
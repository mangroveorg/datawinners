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

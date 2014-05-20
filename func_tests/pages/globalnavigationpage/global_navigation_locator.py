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
DASHBOARD_PAGE_LINK = by_css("a#global_dashboard_link")
DATA_SENDERS_LINK = by_css("a#global_datasenders_link")
SUBJECTS_LINK = by_css("a#global_subjects_link")
PROJECT_LINK = by_css("a#global_projects_link")
ALL_DATA_LINK = by_css("a#global_all_data_link")
SIGN_OUT_LINK = by_css("a[href='/logout/']")
LANGUAGES_LINK = by_id("global_languages_link")

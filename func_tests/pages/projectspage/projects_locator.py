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

PROJECT_LINK_XPATH = "//a[@class='project-id-class' and text()='%s']"
ALL_PROJECTS_TABLE_LINK = by_css("table.all_projects")
CREATE_A_NEW_PROJECT_LINK = by_css("a.button:contains('Create a new project')")
ACTIVATE_PROJECT_LINK_XPATH = "//a[@class='project-id-class' and text()='%s']/../../td[4]/a[text()='Activate']"
PROJECT_STATUS_LABEL_XPATH = "//a[@class='project-id-class' and text()='%s']/../../td[2]"

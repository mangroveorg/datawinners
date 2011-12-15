# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

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

All_DATA_RECORDS_LINK_XPATH = "//a[@class='project-id-class ' and text()='%s']/../../td[4]/span/a[@class!='disable_link' and text()='All Data Records']"
ANALYSIS_LINK_XPATH = "//a[@class='project-id-class ' and text()='%s']/../../td[4]/span/a[@class!='disable_link' and text()='Analysis']"
WEB_SUBMISSION_LINK_XPATH = "//a[@class='project-id-class ' and text()='%s']/../../td[4]/span/a[@class!='disable_link' and text()='Web Submissions']"

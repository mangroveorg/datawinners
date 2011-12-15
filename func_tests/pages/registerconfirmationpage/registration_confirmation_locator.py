# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from framework.utils.common_utils import *

# By default every locator should be CSS

LOCATOR = "locator"
BY = "by"

#Registration Confirmation Page Locator
WELCOME_MESSAGE_LI = by_css("div[class^= 'form']")

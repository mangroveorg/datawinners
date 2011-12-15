from framework.utils.common_utils import *

SUBMIT_BTN = by_css('input[type="submit"]')

QUESTIONS_WITH_ERRORS = by_xpath("//div[@class='answer']//ul[@class='errorlist']/li[normalize-space(text()) != '']")

TRIAL_WEB_LIMIT_REACHED_WARNING_BOX = by_xpath("//div[@class='warning-message-box']//p[normalize-space(text())]")

def get_by_css_name(element_type, element_name):
    return by_css(element_type+"[name="+element_name+"]")
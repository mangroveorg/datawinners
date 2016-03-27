from framework.utils.common_utils import *

SUBMIT_BTN = by_css('input[type="submit"]')

QUESTIONS_WITH_ERRORS = by_xpath("//div[@class='answer']//ul[@class='errorlist']/li[normalize-space(text()) != '']")

TRIAL_WEB_LIMIT_REACHED_WARNING_BOX = by_xpath("//div[@class='warning-message-box']//p[normalize-space(text())]")

SECTION_TITLE = by_css(".section_title")

PROJECT = by_css(".project_name")

BACK_TO_PROJECT_LINK = by_css(".back-to-list")

WEB_NAVIGATION = by_css(".device-navigation .web")

CANCEL = by_id("cancel")

# SUCCESS_MESSAGE = by_css(".success-message-box")

# Locator for Autocomplete functionnal Test
LOCATOR_INPUT = "/%s/%s"
LOCATOR_SELECT1 = "//label[.//input[@name='/%s/%s'] and .='%s']"
LOCATOR_SELECT1_NUMBER = ""
LOCATOR_SELECT1_SHOW_OPTIONS = "form#%s select[name='/%s/%s'] + div button"
LOCATOR_SELECT1_SELECT_VALUE = ""
LOCATOR_SELECT1_MINIMAL_NUMBER = "form#%s select[name='/%s/%s'] + div > ul > li:nth-child(%s)"
LOCATOR_SELECT1_AUTOCOMPLETE_INPUT = "form#%s select[name='/%s/%s'] + input"
LOCATOR_SELECT1_AUTOCOMPLETE_SUGGESTION = "//ul[contains(@class, 'ui-autocomplete') and not(contains(@style,'display: none;'))]/li[@class='ui-menu-item' and @role='menuitem']"
LOCATOR_SELECT1_AUTOCOMPLETE_SUGGESTION_SELECT = "//ul[contains(@class, 'ui-autocomplete') and not(contains(@style,'display: none;'))]/li[@class='ui-menu-item']/a[@class='ui-corner-all' and .='%s']"
LOCATOR_SELECT1_AUTOCOMPLETE_IDNR = by_css("form#questionnaire_for_functional_test_autocomplete select[name='/questionnaire_for_functional_test_autocomplete/select1_idnr_comp'] + input")
LOCATOR_SELECT1_AUTOCOMPLETE__IDNR_INPUT_IN_REPEAT_test = "//section[@name='/%s/%s']/section[.//span[@class='repeat-number' and text()='%s']]/label/select[@name='/%s/%s/%s']/following::input"
LOCATOR_SELECT1_AUTOCOMPLETE__IDNR_INPUT_IN_REPEAT = "//section[@name='/%s/%s']/section[%s]/label/select[@name='/%s/%s/%s']/following::input"
LOCATOR_INPUT_IN_REPEAT = "//section[@name='/%s/%s']/section[%s]/label/input[@name='/%s/%s/%s']"
LOCATOR_ADD_REPEAT_SECTION = "//section[@name='/%s/%s']/section[%s]/div[@class='repeat-buttons']/button[@class='btn btn-default repeat']"
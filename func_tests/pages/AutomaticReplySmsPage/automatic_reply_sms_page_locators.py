from framework.utils.common_utils import by_css, by_xpath

AVAILABLE_LANGUAGES_DROPDOWN_ID = by_css('select#project_language')
NEW_LANGUAGE_CREATE_SELECTOR = by_xpath("//a[contains(text(),'Languages')]")
PROJECT_LANGUAGE_PAGE_SAVE_BUTTON = by_css('#project_language_section input.button')
PROJECT_LANGUAGE_PAGE_SUCCESS_MESSAGE_BOX = by_css('.success-message-box')
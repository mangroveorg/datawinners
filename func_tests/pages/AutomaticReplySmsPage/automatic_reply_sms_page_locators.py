from framework.utils.common_utils import by_css

AVAILABLE_LANGUAGES_DROPDOWN_ID = by_css('select#project_language')
NEW_LANGUAGE_OPTION_SELECTOR = by_css('#project_language option:last-child')
PROJECT_LANGUAGE_PAGE_SAVE_BUTTON = by_css('#project_language_section input.button')
PROJECT_LANGUAGE_PAGE_SUCCESS_MESSAGE_BOX = by_css('.success-message-box')
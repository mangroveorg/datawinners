from framework.utils.common_utils import by_id, by_css

LANGUAGE_SAVE_BUTTON_LOCATOR = by_id("language_save")
LANGUAGE_DROP_DOWN_LOCATOR = by_id("language")
SUCCESS_SUBMISSION_MESSAGE_LOCATOR = by_id("custom_message0")
SUBMISSION_WITH_ERROR_MESSAGE_LOCATOR = by_id("custom_message1")
SUBMISSION_WITH_INCORRECT_NUMBER_OF_RESPONSES_LOCATOR = by_id("custom_message2")
SUBMISSION_WITH_INCORRECT_UNIQUE_ID = by_id("custom_message3")
RESPONSE_ERROR_MESSAGE_FROM_UNAUTHORIZED_SOURCE_LOCATOR = by_id("custom_message4")
NEW_LANGUAGE_INPUT_BOX = by_css('#add_new_language_pop input')
ADD_NEW_LANG_CONFIRM_BUTTON = by_css('#add_new_language_pop .yes_button')
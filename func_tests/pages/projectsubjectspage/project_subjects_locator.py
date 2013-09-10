from framework.utils.common_utils import by_css, by_id, by_xpath

EDIT_FORM_LINK = by_css("#my_subjects_links a.edit-form-link")
EDIT_CONTINUE_LINK = by_id("edit_ok")
ADD_QUESTION_LINK = by_css(".add_link")
SELECTED_QUESTION_LABEL = by_css(".question_selected>a")
SUBMIT_BTN = by_id("submit-button")
SUCCESS_MESSAGE_TIP = by_css(".success-message-box")
TYPE_CB = by_css("[name=type]")
ACTION_DROP_DOWN = by_css("#subjects_table_wrapper button.action")
EDIT_LI_LOCATOR = by_xpath("//a[@id='edit']/parent::li")
NONE_SELECTED_LOCATOR = by_id("none-selected")
ACTION_MENU = by_id("action")
EMPTY_ACTION_MENU = by_id("none-selected")
MY_SUBJECTS_TAB_LINK = by_css("#my_subjects ul.secondary_tab li:first-child a")
SUBJECT_CB_LOCATOR = "#subjects_table_wrapper tbody tr td:first-child input#%s"
CHECKALL_CB = by_id("checkall-checkbox")
SPECIFIC_TYPE_CB_BY_CSS = "[name=type][value=%s]"
REGISTER_SUBJECT_LINK=by_id('register_subjects')
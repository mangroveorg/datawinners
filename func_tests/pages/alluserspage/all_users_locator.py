from framework.utils.common_utils import *

CHECK_ALL_USERS_LOCATOR = by_css("#check_all_users")
ALL_USERS_ACTION_SELECT = by_css(".action")
ERROR_CONTAINER = by_css("div#error")
CONFIRM_DELETE_BUTTON = by_css("#delete_user_warning_dialog a.yes_button")
CANCEL_DELETE_BUTTON = by_css("#delete_user_warning_dialog a.no_button")
MESSAGES_CONTAINER = by_css("span.message-span")
CHECK_NTH_USER_LOCATOR = "#users_list table tbody tr:nth-child(%s) td:nth-child(1) input"
ADD_USER_LINK = by_css("a[href='/account/user/new/']")
ACTION_MENU = by_id("action")
from framework.utils.common_utils import by_css, by_id

SMS_CONTENT_TB = by_css("#sms_content")
SEND_BROADCAST_SMS_BTN = by_css("input#id_send_broadcast_sms_button")
SEND_TO_SELECT = by_css("#id_to")
SEND_TO_TB = by_css("#id_others")
OTHER_PEOPLE_HELP_TEXT = by_css("#additional_people_column .black_italic")
OTHER_PEOPLE_ERROR_TEXT_BY_CSS = by_css("#additional_people_column .error_arrow label.error")
NUMBER_OF_ANONYMOUS_AND_ASSOCIATED_RECIPIENTS_TEXT_BY_CSS= by_css("#AllSubmitted span")
NUMBER_OF_ASSOCIATED_RECIPIENTS_TEXT_BY_CSS= by_css("#Associated span")
DROP_DOWN = by_css("#input_to .dropdown-toggle")
SEND_TO_DDCL = by_css("#input_to > span")
OTHER_PEOPLE_OPTION_DDCL = by_id("Additional")
REPLY_SMS_LINK = by_css('#reply_sms_tab')
from framework.utils.common_utils import by_css

CANCEL_LINK = by_css('div.ui-dialog[style*="block"] > div.ui-dialog-content > div > a.no_button')

CONFIRM_LINK = by_css('div.ui-dialog[style*="block"] > div.ui-dialog-content > div > a.yes_button')

MESSAGE_LINK = by_css('div.ui-dialog[style*="block"] > div.ui-dialog-content > .warning_message')

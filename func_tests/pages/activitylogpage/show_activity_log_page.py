# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time
from framework.utils.common_utils import by_css
from pages.page import Page
from pages.activitylogpage.show_activity_log_locator import *


class ShowActivityLogPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def get_data_on_cell(self, row=0, column=0):
        locator = by_css(FIND_DATA_BY_ROW_AND_COLUMN_NUMBER % (row, column))
        return self.driver.find(locator).text
from framework.utils.common_utils import by_css
from pages.page import Page


class ReportsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def navigate_to_report(self, report_name):
        report_tabs = self.driver.find_elements_(by_css("#report_navigation a"))
        for report_tab in report_tabs:
            if report_tab.text == report_name:
                report_tab.click()
                break
        return self

    def get_number_of_records(self):
        data_rows = self.driver.find_elements_(by_css("#report_container tr"))
        # reducing length by 1 for discounting header from total number of table rows.
        return len(data_rows) - 1

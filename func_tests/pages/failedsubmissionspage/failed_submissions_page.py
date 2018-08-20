from framework.utils.common_utils import by_xpath, by_id, by_css
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT

class FailedSubmissionsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def get_total_number_of_entries(self):
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_id("failedsubmissions_table_processing"))
        #return int(self.driver.execute_script("return $('table tbody tr').length - 1"))
        try:
            return int(self.driver.execute_script("return $('.dataTables_info').html().split(' ')[5]"))
        except Exception:
            return int(self.driver.execute_script("return $('.dataTables_info').html().split(' ')[4]"))

    def get_entry_for_row_number(self, row_number):
        locator = "#failedsubmissions_table tbody tr:nth-child(%d) td:nth-child(%d)"
        questionnaire_code = self.driver.find(by_css(locator % (row_number + 1, 4))).text
        from_number = self.driver.find(by_css(locator % (row_number + 1, 2))).text
        to_number = self.driver.find(by_css(locator % (row_number + 1, 3))).text
        message = self.driver.find(by_css(locator % (row_number + 1, 5))).text
        error = self.driver.find(by_css(locator % (row_number + 1, 6))).text
        return {
            'questionnaire_code': questionnaire_code,
            'from_number': from_number,
            'to_number': to_number,
            'message': message,
            'error': error
        }
from framework.utils.common_utils import by_xpath
from pages.page import Page

class FailedSubmissionsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def get_total_number_of_entries(self):
        return int(self.driver.execute_script("return $('table tr').length - 1"))

    def get_entry_for_row_number(self, row_number):
        questionnaire_code = self.driver.find(by_xpath(".//*/tr[%d]/td[1]" % row_number)).text
        from_number = self.driver.find(by_xpath(".//*/tr[%d]/td[2]" % row_number)).text
        to_number = self.driver.find(by_xpath(".//*/tr[%d]/td[3]" % row_number)).text
        message = self.driver.find(by_xpath(".//*/tr[%d]/td[4]" % row_number)).text
        error = self.driver.find(by_xpath(".//*/tr[%d]/td[5]" % row_number)).text
        return {
            'questionnaire_code': questionnaire_code,
            'from_number': from_number,
            'to_number': to_number,
            'message': message,
            'error': error
        }
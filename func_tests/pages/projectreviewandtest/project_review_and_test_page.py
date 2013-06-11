from selenium.webdriver.support import ui
from pages.page import Page
from pages.projectreviewandtest.project_review_and_test_locator import *

class ProjectReviewTestPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def get_reminder_status(self):
        self.driver.find(REMINDER_SECTION).click()
        wait = ui.WebDriverWait(self.driver,15)
        wait.until(lambda driver: driver.find(REMINDER_STATUS).text)
        return self.driver.find(REMINDER_STATUS).text
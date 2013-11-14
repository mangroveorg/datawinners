from pages.expiredtrialpage.expired_trail_locator import EXPIRED_TRIAL_ACCOUNT_MESSAGE, SUBSCRIBE_NOW
from pages.page import Page

class ExpiredTrialPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def get_error_message(self):
     """
     Function to fetch the error messages from error label of the login
     page

     Return error message
     """
     error_message = ""
     locators = self.driver.find_elements_(EXPIRED_TRIAL_ACCOUNT_MESSAGE)
     if locators:
         for locator in locators:
             error_message = error_message + locator.text
     return error_message.replace("\n", " ")

    def get_subscribe_button(self):
        return self.driver.find(SUBSCRIBE_NOW).get_attribute("href")
    

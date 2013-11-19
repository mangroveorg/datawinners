from pages.page import Page
from pages.registrationpage.registration_page import RegistrationPage
from tests.registrationtests.registration_data import *
from pages.upgradepage.upgrade_page_locator import *

class UpgradePage(RegistrationPage):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def click_submit_button(self):
        self.driver.find(ORGANIZATION_UPGRADE_BTN).click()

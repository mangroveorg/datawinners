from pages.page import Page
from pages.smartphoneinstructionpage.smart_phone_instruction_locator import SMART_PHONE_INSTRUCTION


class SmartPhoneInstructionPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def get_smart_phone_instruction(self):
        return self.driver.find(SMART_PHONE_INSTRUCTION)

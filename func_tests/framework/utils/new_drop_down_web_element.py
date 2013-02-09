# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from selenium.webdriver.remote.webelement import WebElement
import time


class NewDropDown(WebElement):
    def __init__(self, dropDownWebElement):
        super(NewDropDown, self).__init__(dropDownWebElement.parent, dropDownWebElement.id)
        self.webElement = dropDownWebElement
#        self.selectOptions = self.webElement.find_elements_by_id("action_dropdown")
        self.selectOptions = "something"

    def get_options(self):
        """Gets the list of options in the drop down
        """
        return [option.get_text() for option in self.selectOptions]

    def get_selected(self):
        """ Gets the currently selected item in the drop down
        """
        for option in self.selectOptions:
            if option.is_selected():
                return option.get_attribute("value")
        return None

    def is_selected(self, itemText):
        """ Gets the currently selected item from the drop down
        """
        for option in self.selectOptions:
            if option.get_text() == itemText:
                return option.is_selected()
        return False

    def set_selected(self, itemText):
        """ Selects the provided itemText in the drop down
        """
        for option in self.selectOptions:
            value = option.get_attribute("value")
            if value == itemText:
                option.click()
                break

    def click_on_action_button(self, itemText):
            """ Selects the provided itemText in the drop down
            """

            self.webElement.click()


    def set_selected_by_text(self, itemText):
        """ Selects the provided itemText in the drop down
        """
        for option in self.selectOptions:
            value = option.text
            if value == itemText:
                option.click()
                break



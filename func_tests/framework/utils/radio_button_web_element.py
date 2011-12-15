# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from selenium.webdriver.remote.webelement import WebElement


class RadioButton(WebElement):
    def __init__(self, radioButttonWebElement):
        super(RadioButton, self).__init__(radioButttonWebElement.parent, radioButttonWebElement.id)
        self.webElement = radioButttonWebElement

    def is_enabled(self):
        return self.webElement.is_enabled()

    def is_selected(self):
        return self.webElement.is_selected()

    def set_selected(self):
        return self.webElement.select()

    def click(self):
        return self.webElement.click()

    def radio_button_status(self):
        return self.webElement.is_enabled()

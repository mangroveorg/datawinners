# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from selenium.webdriver.remote.webelement import WebElement


class Button(WebElement):
    def __init__(self, buttonWebElement):
        super(Button, self).__init__(buttonWebElement.parent, buttonWebElement.id)
        self.webElement = buttonWebElement

    def is_enabled(self):
        return self.webElement.is_enabled()

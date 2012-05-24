# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webelement import WebElement

class LightBox(WebElement):
    def __init__(self, lightBoxWebElement):
        super(LightBox, self).__init__(lightBoxWebElement.parent, lightBoxWebElement.id)
        self.webElement = lightBoxWebElement

    def enter_text(self, textToBeEntered):
        try:
            self.webElement.click()
            self.webElement.clear()
        except WebDriverException:
            pass
        self.webElement.send_keys(textToBeEntered)
        return self

    def is_enabled(self):
        return self.webElement.is_enabled()
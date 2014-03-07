# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from tests.testsettings import WAIT


class Page(object):
    def __init__(self, driver):
        self.driver = driver
        self.url = self.driver.current_url
        self.driver.implicitly_wait(WAIT)

    def switch_language(self, language):
        from framework.utils.common_utils import by_css
        locator = by_css("a[href='/switch/%s/']" % language)
        self.driver.find(locator).click()

    def refresh(self):
        self.driver.refresh()


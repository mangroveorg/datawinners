# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from tests.testsettings import WAIT


class Page(object):
    def __init__(self, driver):
        self.driver = driver
        self.url = self.driver.current_url
        self.driver.implicitly_wait(WAIT)

# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
import sys
from datawinners import settings

from framework.drivers.driver_wrapper import DriverWrapper
from tests.testsettings import CLOSE_BROWSER_AFTER_TEST


def setup_driver(browser=None):
    driver = DriverWrapper(browser)
    return driver


def teardown_driver(driver):
    try:
        if CLOSE_BROWSER_AFTER_TEST:
            driver.quit()
    except TypeError:
        pass


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.driver = setup_driver()

    def tearDown(self):
        teardown_driver(self.driver)


def is_running_in_pycharm():
    return 'pycharm' in sys.argv[0]


class HeadlessRunnerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        browser = "phantom"
        if is_running_in_pycharm():
            browser = settings.DEBUG_BROWSER or "firefox"
        cls.driver = setup_driver(browser)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def tearDown(self):
        exception_info = sys.exc_info()
        if exception_info != (None, None, None):
            import os

            if not os.path.exists("screenshots"):
                os.mkdir("screenshots")
            self.driver.get_screenshot_as_file(
                "screenshots/screenshot-%s-%s.png" % (self.__class__.__name__, self._testMethodName))

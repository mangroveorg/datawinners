# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from framework.drivers.driver_wrapper import DriverWrapper, get_default_browser_name
from tests.testsettings import CLOSE_BROWSER_AFTER_TEST, WAIT


def setup_driver(browser=get_default_browser_name()):
    driver = DriverWrapper(browser)
    driver.implicitly_wait(WAIT)
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

if __name__ == "__main__":
    unittest.main()

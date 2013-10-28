# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from framework.drivers.driver_wrapper import DriverWrapper
from tests.testsettings import CLOSE_BROWSER_AFTER_TEST, WAIT


def setup_driver():
    driver = DriverWrapper()
    driver.implicitly_wait(WAIT)
    return driver

def teardown_driver(driver):
    try:
        if CLOSE_BROWSER_AFTER_TEST:
            driver.quit()
    except TypeError as e:
        pass

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.driver = setup_driver()

    def tearDown(self):
        teardown_driver(self.driver)

if __name__ == "__main__":
    unittest.main()

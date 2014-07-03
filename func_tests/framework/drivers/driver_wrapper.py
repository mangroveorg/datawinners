# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os
import sys
import datetime

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

from framework.exception import ElementStillPresentException, CouldNotLocatePageException, ElementFoundWithoutDesiredVisibility, CouldNotLocateElementException
from framework.utils.common_utils import by_css
from framework.utils.drop_down_web_element import DropDown
from framework.utils.new_drop_down_web_element import NewDropDown
from framework.utils.text_box_web_element import TextBox
from framework.utils.radio_button_web_element import RadioButton
from tests.testsettings import UI_TEST_TIMEOUT

LOCATOR = "locator"
BY = "by"


def get_default_browser_name():
    import sys

    if os.system('which chromium-browser> /dev/null') == os.EX_OK:
        sys.stderr.write("chromedriver found, using chrome as the browser\n")
        return "chrome"
    else:
        sys.stderr.write("chromedriver not found, falling back to firefox\n")
        return "firefox"


def get_driver_for_browser(browser):
    browser = browser if browser else get_default_browser_name()
    sys.stderr.write("using driver for browser: %s\n" % browser)
    if browser == "firefox":
        fprofile = FirefoxProfile()
        driver = webdriver.Firefox(fprofile)
    elif browser == "ie":
        driver = webdriver.Ie()
    elif browser == "chrome":
        capabilities = dict(DesiredCapabilities.CHROME, **{
            'chrome.switches': ["--incognito"]
        })
        driver = webdriver.Chrome(executable_path='/home/ashwin/Downloads/chromedriver',
                                  desired_capabilities=capabilities)
    elif browser == "htmlunit":
        driver = webdriver.Remote()
    elif browser == "phantom":
        driver = webdriver.PhantomJS()
    elif browser == "remoteie":
        driver = webdriver.Remote(command_executor="http://localhost:5555/", desired_capabilities=DesiredCapabilities.INTERNETEXPLORER)
    else:
        raise NotImplemented("Unknown browser " + browser)
    driver.maximize_window()
    return driver


class DriverWrapper(object):
    """
    DriverWrapper class is for creating an wrapper over traditional webdriver
     class. To do some additional function on different web elements
    """

    def __init__(self, browser=None):
        self._driver = get_driver_for_browser(browser)
        self._driver.implicitly_wait(UI_TEST_TIMEOUT)
        self._driver.set_window_size(1600,900)
        self._driver.delete_all_cookies()

    def find_drop_down(self, locator_dict):
        """
        Create DropDown class object with the given web element

        Args:
        locator_dict is the dictionary of the locator which contains key
        values like {"locator":"input[name='email']","by":"By.CSS_SELECTOR"}

        Return DropDown
        """
        return DropDown(self.find(locator_dict))

    def find_new_drop_down(self, locator_dict):
        """
        Create DropDown class object with the given web element

        Args:
        locator_dict is the dictionary of the locator which contains key
        values like {"locator":"input[name='email']","by":"By.CSS_SELECTOR"}

        Return DropDown
        """
        return NewDropDown(self.find(locator_dict))

    def find_text_box(self, locator_dict):
        """
        Create TextBox class object with the given web element

        Args:
        locator_dict is the dictionary of the locator which contains key
        values like {"locator":"input[name='email']","by":"By.CSS_SELECTOR"}

        Return TextBox
        """
        return TextBox(self.find(locator_dict))

    def get_input_value(self, locator_dict):
        """
        Get value of a input field
        """
        return self.find(locator_dict).get_attribute("value")

    def find_radio_button(self, locator_dict):
        """
        Create RadioButton class object with the given web element

        Args:
        locator_dict is the dictionary of the locator which contains key
        values like {"locator":"input[name='email']","by":"By.CSS_SELECTOR"}

        Return RadioButton
        """
        return RadioButton(self.find(locator_dict))

    def create_screenshot(self, filename="error_screen_shot.png"):
        if not os.path.exists("screenshots"):
            os.mkdir("screenshots")
        self._driver.save_screenshot("screenshots/%s" % filename)

    def find(self, locator_dict):
        """
        Finds element on the web page using locator dictionary

        Args:
        locator_dict is the dictionary of the locator which contains key
        values like {"locator":"input[name='email']","by":"By.CSS_SELECTOR"}

        Return webelement
        """
        try:
            return self._driver.find_element(by=locator_dict[BY], value=locator_dict[LOCATOR])
        except NoSuchElementException as e:
            self.create_screenshot()
            raise CouldNotLocateElementException(selector=locator_dict[BY], locator=locator_dict[LOCATOR])

    def find_elements_(self, locator_dict):
        """
        Finds elements on the web page using locator dictionary

        Args:
        locator_dict is the dictionary of the locator which contains key
        values like {"locator":"input[name='email']","by":"By.CSS_SELECTOR"}

        Return list of webelement
        """
        return self._driver.find_elements(by=locator_dict[BY],
                                          value=locator_dict[LOCATOR])

    def find_visible_element(self, locator_dict):
        """
        Finds element which are visible on the web page using locator dictionary

        Args:
        locator_dict is the dictionary of the locator which contains key
        values like {"locator":"input[name='email']","by":"By.CSS_SELECTOR"}

        Return first element of visible webelements
        """

        return self.find_visible_elements_(locator_dict)[0] or None

    def find_visible_elements_(self, locator_dict):
        """
        Finds elements which are visible on the web page using locator dictionary

        Args:
        locator_dict is the dictionary of the locator which contains key
        values like {"locator":"input[name='email']","by":"By.CSS_SELECTOR"}

        Return list of webelement
        """
        elements = self._driver.find_elements(by=locator_dict[BY], value=locator_dict[LOCATOR])
        return [element for element in elements if element.is_displayed()]

    def go_to(self, url):
        """Open URL using get command of webdriver api"""
        self._driver.get(url)

    def get_title(self):
        """Get the title of the web page"""
        return self._driver.title

    def is_element_present(self, element_locator):
        try:
            locator = self.find(element_locator)
            return locator
        except CouldNotLocateElementException:
            return False

    def wait_until_modal_dismissed(self):
        self.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".loading"))

    def wait_for_element(self, time_out_in_seconds, object_id, want_visible=None):
        """Finds elements by their id by waiting till timeout.

        Note that implicitly_wait mostly largely eliminates the need for this"""

        current_time = datetime.datetime.now()
        end_time = current_time + datetime.timedelta(0, time_out_in_seconds)

        while True:
            try:
                element = self.find(object_id)
                current_time = datetime.datetime.now()

                if want_visible is None or element.is_displayed() == want_visible:
                    return element
                elif current_time >= end_time:
                    message = "Expected visibility %s for element %s -- found %s after %s seconds" % (
                        want_visible, object_id, element.is_displayed(), time_out_in_seconds)
                    raise ElementFoundWithoutDesiredVisibility(message)
            except CouldNotLocateElementException as ne:
                current_time = datetime.datetime.now()
                if current_time >= end_time:
                    self.create_screenshot()
                    raise ne

    def wait_for_page_load(self):
        WebDriverWait(self._driver, UI_TEST_TIMEOUT).until(lambda driver:  u"complete" == driver.execute_script("return document.readyState"))

    def wait_for_page_with_title(self, time_out_in_seconds, title):
        current_time = datetime.datetime.now()
        end_time = current_time + datetime.timedelta(0, time_out_in_seconds)

        while True:
            if self.title == title:
                return title
            else:
                current_time = datetime.datetime.now()
                if current_time >= end_time:
                    raise CouldNotLocatePageException(
                        "Could not locate page with title %s after %s seconds" % (title, time_out_in_seconds))

    def __getattr__(self, item):
        return getattr(self._driver, item)

    def wait_until_element_is_not_present(self, time_out_in_seconds, locator):
        current_time = datetime.datetime.now()
        end_time = current_time + datetime.timedelta(0, time_out_in_seconds)

        while True:
            try:
                element = self.find(locator)
                if element and not element.is_displayed():
                    return True
                else:
                    current_time = datetime.datetime.now()
                    if current_time >= end_time:
                        raise ElementStillPresentException("Timer expired and %s is still present" % locator)
            except CouldNotLocateElementException:
                return
            except StaleElementReferenceException:
                return


    def wait_until_web_element_is_not_present(self, time_out_in_seconds, element):
        current_time = datetime.datetime.now()
        end_time = current_time + datetime.timedelta(0, time_out_in_seconds)

        while True:
            try:
                if element and not element.is_displayed():
                    return True
                else:
                    current_time = datetime.datetime.now()
                    if current_time >= end_time:
                        raise ElementStillPresentException("Timer expired and element is still present" )
            except CouldNotLocateElementException:
                return
            except StaleElementReferenceException:
                return


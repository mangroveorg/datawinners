from nose.plugins.attrib import attr
from pages.loginpage.login_page import LoginPage
from tests.editdatasendertests.edit_datasender_data import *
from pages.adddatasenderspage.add_data_senders_page import AddDataSenderPage
from framework.base_test import setup_driver, teardown_driver
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
import time, unittest

@attr('suit_1')
class TestEditDataSender(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)


    @attr('functional_test')
    def test_should_not_able_to_use_other_datasender_mobile_number(self):
        self.driver.go_to(EDIT_DATASENDER_PAGE)
        page = AddDataSenderPage(self.driver)
        page.enter_datasender_mobile_number("1234567890")
        page.click_submit_button()
        time.sleep(2)
        self.assertEqual(page.get_error_message(),
            u'Mobile Number Sorry, the telephone number 1234567890 has already been registered.')
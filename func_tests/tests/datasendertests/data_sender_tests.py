from framework.base_test import BaseTest
from pages.datasenderpage.data_sender_page import DataSenderPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import DATA_SENDER_CREDENTIALS

class DataSenderTest(BaseTest):

    def test_send_in_data_to_a_project(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with(DATA_SENDER_CREDENTIALS)
        data_sender_page = DataSenderPage(self.driver)
        web_submission_page = data_sender_page.send_in_data()
        self.assertEqual(web_submission_page.get_title(), "Data Submission")



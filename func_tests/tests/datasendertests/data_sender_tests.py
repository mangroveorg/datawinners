from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.datasenderpage.data_sender_page import DataSenderPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.datasendertests.data_sender_data import PAGE_TITLE, SECTION_TITLE
from tests.logintests.login_data import DATA_SENDER_CREDENTIALS
from tests.websubmissiontests.web_submission_data import DEFAULT_ORG_DATA, PROJECT_NAME

class DataSenderTest(BaseTest):

    def test_send_in_data_to_a_project(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with(DATA_SENDER_CREDENTIALS)
        data_sender_page = DataSenderPage(self.driver)
        web_submission_page = data_sender_page.send_in_data()
        self.assertEquals(web_submission_page.get_title(), PAGE_TITLE)
        self.assertEquals(web_submission_page.get_section_title(), SECTION_TITLE)
        self.assertEquals(web_submission_page.get_project_name(), fetch_(PROJECT_NAME, from_(DEFAULT_ORG_DATA)))



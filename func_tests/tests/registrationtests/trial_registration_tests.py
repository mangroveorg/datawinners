from nose.plugins.attrib import attr
from framework.base_test import BaseTest, HeadlessRunnerTest
from framework.utils.common_utils import by_css
from framework.utils.database_manager_postgres import DatabaseManager
from pages.registrationpage.registration_page import RegistrationPage
from testdata.test_data import DATA_WINNER_REGISTER_TRIAL_PAGE, DATA_WINNER_HOMEPAGE, DATA_WINNER_EN_PRICING_PAGE, DATA_WINNER_TRIAL_ACCOUNT_EXPIRED_PAGE
from tests.registrationtests.registration_data import REGISTRATION_DATA_FOR_SUCCESSFUL_TRIAL_REGISTRATION, REGISTRATION_SUCCESS_MESSAGE, ORGANIZATION_SECTOR_DROP_DOWN_LIST, INVALID_EMAIL_ERROR_MESSAGE, \
    REGISTRATION_DATA_FOR_UNSUCCESSFUL_TRIAL_REGISTRATION


def register_and_get_email_for_trial(driver):
    driver.go_to(DATA_WINNER_REGISTER_TRIAL_PAGE)
    registration_page = RegistrationPage(driver)
    registration_confirmation_page, email = registration_page.successful_registration_with(
        REGISTRATION_DATA_FOR_SUCCESSFUL_TRIAL_REGISTRATION)
    return registration_confirmation_page, email


class TestTrialRegistrationPage(HeadlessRunnerTest):
    @attr('functional_test')
    def test_register_trial_organization(self):
        registration_confirmation_page, email = register_and_get_email_for_trial(self.driver)
        self.assertEqual(registration_confirmation_page.registration_success_message(), REGISTRATION_SUCCESS_MESSAGE)
        #dbmanager = DatabaseManager()
        #dbmanager.delete_organization_all_details(email)

    @attr('functional_test')
    def test_trial_link_from_homepage(self):
        self.driver.go_to(DATA_WINNER_HOMEPAGE)
        self.driver.find(by_css("a.intro_try_button")).click()
        self.driver.wait_for_page_with_title(10, "Register")
        self.assertEqual(self.driver.current_url, DATA_WINNER_REGISTER_TRIAL_PAGE)

    @attr('functional_test')
    def test_trial_link_from_pricing_page(self):
        self.driver.go_to(DATA_WINNER_EN_PRICING_PAGE)
        self.driver.find(by_css("ul.obox-grid li:first-child.obox-column a.try_button")).click()
        self.driver.wait_for_page_with_title(10, "Register")
        self.assertEqual(self.driver.current_url, "https://app.datawinners.com/register/trial/")

    @attr('functional_test')
    def test_register_organization_sector_have_the_right_select_options(self):
        self.driver.go_to(DATA_WINNER_REGISTER_TRIAL_PAGE)
        sectors_drop_down = self.driver.find_drop_down(ORGANIZATION_SECTOR_DROP_DOWN_LIST)
        self.assertIn('Please Select', sectors_drop_down.text)
        self.assertIn('Food Security', sectors_drop_down.text)
        self.assertIn('Other', sectors_drop_down.text)

    @attr('functional_test')
    def test_content_box_exist_in_trial_account_expired_page(self):
        self.driver.go_to(DATA_WINNER_TRIAL_ACCOUNT_EXPIRED_PAGE)
        about_datawinners_box = self.driver.find_elements_(by_css("h5"))
        self.assertEqual('About DataWinners', about_datawinners_box[0].text)
        self.assertEqual('Subscription Details', about_datawinners_box[1].text)

    @attr('functional_test')
    def test_user_focus_must_be_on_email_field(self):
        self.driver.go_to(DATA_WINNER_REGISTER_TRIAL_PAGE)
        registration_page = RegistrationPage(self.driver)
        registration_page.register_with(REGISTRATION_DATA_FOR_UNSUCCESSFUL_TRIAL_REGISTRATION)
        self.assertEqual(registration_page.get_error_message(), INVALID_EMAIL_ERROR_MESSAGE)
        a = self.driver.switch_to_active_element()
        self.assertEqual(a.get_attribute("id"), u"id_email")
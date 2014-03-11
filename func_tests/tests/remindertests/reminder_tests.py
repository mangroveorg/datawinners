from unittest import TestCase
from nose.plugins.attrib import attr
from framework.base_test import BaseTest, setup_driver
from framework.exception import CouldNotLocateElementException
from framework.utils.common_utils import by_css
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, LOGOUT
from tests.logintests.login_data import TRIAL_CREDENTIALS_VALIDATES, VALID_CREDENTIALS
from tests.remindertests.reminder_data import *
from framework.utils.data_fetcher import fetch_, from_

@attr('suit_3')
class TestReminderSend(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver(browser="phantom")

    def tearDown(self):
        self.driver.go_to(LOGOUT)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def login_if_needed(self, account):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        if self.driver.is_element_present(by_css("span.welcome")):
            return GlobalNavigationPage(self.driver)
        login_page = LoginPage(self.driver)
        return login_page.do_successful_login_with(account)

    def go_to_reminder_page(self, project, credentials):
        global_navigation = self.login_if_needed(credentials)
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        overview_page = all_project_page.navigate_to_project_overview_page(project)
        return overview_page.navigate_to_reminder_page()

    def set_deadline_by_month(self, reminder_settings, deadline):
        reminder_settings.set_frequency(fetch_(FREQUENCY, from_(deadline)))
        reminder_settings.set_month_day(fetch_(DAY, from_(deadline)))
        reminder_settings.set_deadline_type_for_month(fetch_(TYPE, from_(deadline)))
        return reminder_settings

    @attr("functional_test")
    def test_trial_account_should_see_reminder_not_work_message_at_reminder_tab_in_active_project(self):
        self.driver.go_to(LOGOUT)
        all_reminder_pages = self.go_to_reminder_page(fetch_(PROJECT_NAME, from_(DISABLED_REMINDER)), TRIAL_CREDENTIALS_VALIDATES)
        self.assertEqual(DISABLED_REMINDER[WARNING_MESSAGE], all_reminder_pages.get_warning_message())
        all_reminder_pages.click_sent_reminder_tab()
        self.assertEqual(fetch_(WARNING_MESSAGE, from_(DISABLED_REMINDER)), all_reminder_pages.get_warning_message())

    @attr("functional_test")
    def test_verify_change_in_deadline_example_for_week(self):
        all_reminder_pages = self.go_to_reminder_page(fetch_(PROJECT_NAME, from_(DEADLINE_FIRST_DAY_OF_SAME_WEEK)), VALID_CREDENTIALS)
        reminder_settings = all_reminder_pages.click_reminder_settings_tab()
        reminder_settings = all_reminder_pages.set_deadline_by_week(reminder_settings, fetch_(DEADLINE, from_(DEADLINE_FIRST_DAY_OF_SAME_WEEK)))
        self.assertEqual(reminder_settings.get_example_text(), fetch_(DEADLINE, from_(DEADLINE_FIRST_DAY_OF_SAME_WEEK))[EXAMPLE_TEXT])

        reminder_settings = all_reminder_pages.set_deadline_by_week(reminder_settings, fetch_(DEADLINE, from_(DEADLINE_LAST_DAY_OF_SAME_WEEK)))
        self.assertEqual(reminder_settings.get_example_text(), fetch_(EXAMPLE_TEXT, from_(DEADLINE_LAST_DAY_OF_SAME_WEEK[DEADLINE])))

        reminder_settings = all_reminder_pages.set_deadline_by_week(reminder_settings, fetch_(DEADLINE, from_(DEADLINE_SECOND_DAY_OF_FOLLOWING_WEEK)))
        self.assertEqual(reminder_settings.get_example_text(), fetch_(EXAMPLE_TEXT, from_(DEADLINE_SECOND_DAY_OF_FOLLOWING_WEEK[DEADLINE])))

        reminder_settings = all_reminder_pages.set_deadline_by_week(reminder_settings, fetch_(DEADLINE, from_(DEADLINE_FIFTH_DAY_OF_FOLLOWING_WEEK)))
        self.assertEqual(reminder_settings.get_example_text(), fetch_(EXAMPLE_TEXT, from_(DEADLINE_FIFTH_DAY_OF_FOLLOWING_WEEK[DEADLINE])))

    @attr("functional_test")
    def test_verify_change_in_deadline_example_for_month(self):
        all_reminder_pages = self.go_to_reminder_page(fetch_(PROJECT_NAME, from_(DEADLINE_FIRST_DAY_OF_SAME_MONTH)), VALID_CREDENTIALS)
        reminder_settings = all_reminder_pages.click_reminder_settings_tab()

        reminder_settings = self.set_deadline_by_month(reminder_settings, fetch_(DEADLINE, from_(DEADLINE_FIRST_DAY_OF_SAME_MONTH)))
        self.assertEqual(reminder_settings.get_example_text(), fetch_(EXAMPLE_TEXT, from_(DEADLINE_FIRST_DAY_OF_SAME_MONTH[DEADLINE])))

        reminder_settings = self.set_deadline_by_month(reminder_settings, fetch_(DEADLINE, from_(DEADLINE_LAST_DAY_OF_SAME_MONTH)))
        self.assertEqual(reminder_settings.get_example_text(), fetch_(EXAMPLE_TEXT, from_(DEADLINE_LAST_DAY_OF_SAME_MONTH[DEADLINE])))

        reminder_settings = self.set_deadline_by_month(reminder_settings, fetch_(DEADLINE, from_(DEADLINE_TWENTIETH_DAY_OF_FOLLOWING_MONTH)))
        self.assertEqual(reminder_settings.get_example_text(), fetch_(EXAMPLE_TEXT, from_(DEADLINE_TWENTIETH_DAY_OF_FOLLOWING_MONTH[DEADLINE])))

        reminder_settings = self.set_deadline_by_month(reminder_settings, fetch_(DEADLINE, from_(DEADLINE_ELEVENTH_DAY_OF_FOLLOWING_MONTH)))
        self.assertEqual(reminder_settings.get_example_text(), fetch_(EXAMPLE_TEXT, from_(DEADLINE_ELEVENTH_DAY_OF_FOLLOWING_MONTH[DEADLINE])))

    @attr("functional_test")
    def test_verify_set_one_reminder(self):
        all_reminder_pages = self.go_to_reminder_page(fetch_(PROJECT_NAME, from_(REMINDER_DATA_WEEKLY)), VALID_CREDENTIALS)
        reminder_settings = all_reminder_pages.click_reminder_settings_tab()
        reminder_settings = all_reminder_pages.set_deadline_by_week(reminder_settings, fetch_(DEADLINE, from_(REMINDER_DATA_WEEKLY)))
        reminder_settings.set_reminder(fetch_(REMINDERS, from_(REMINDER_DATA_WEEKLY)))
        reminder_settings.set_whom_to_send(fetch_(WHOM_TO_SEND, from_(REMINDER_DATA_WEEKLY)))
        reminder_settings.save_reminders()
        self.assertEqual(reminder_settings.get_success_message(), SUCCESS_MESSAGE)
        reminders = reminder_settings.get_reminders_of_project(reminder_settings.get_project_id())
        self.assertEqual(fetch_(REMINDERS, from_(REMINDER_DATA_WEEKLY)), reminders[0])

    @attr("functional_test")
    def test_should_display_sms_character_length_for_various_reminder_types(self):
        all_reminder_pages = self.go_to_reminder_page(fetch_(PROJECT_NAME, from_(DEADLINE_FIRST_DAY_OF_SAME_MONTH)), VALID_CREDENTIALS)
        self.display_sms_length_for_a_reminder_type(all_reminder_pages, "before")
        self.display_sms_length_for_a_reminder_type(all_reminder_pages, "on")
        self.display_sms_length_for_a_reminder_type(all_reminder_pages, "after")


    @attr('functional_test')
    def test_should_limit_sms_character_length_to_160_for_all_reminder_types(self):
        all_reminder_pages = self.go_to_reminder_page(fetch_(PROJECT_NAME, from_(DEADLINE_FIRST_DAY_OF_SAME_MONTH)), VALID_CREDENTIALS)
        self.limit_sms_length_for_a_reminder_type(all_reminder_pages, "before")
        self.limit_sms_length_for_a_reminder_type(all_reminder_pages, "on")
        self.limit_sms_length_for_a_reminder_type(all_reminder_pages, "after")

    def limit_sms_length_for_a_reminder_type(self, all_reminder_pages, reminder_type):
        reminder_settings = all_reminder_pages.click_reminder_settings_tab()
        getattr(reminder_settings, "enable_%s_deadline_reminder" % reminder_type)()
        getattr(reminder_settings, "set_message_for_%s_deadline_reminder" % reminder_type)(MESSAGE_LONGER_THAN_160)
        length = reminder_settings.get_sms_text_length_for_a_reminder_type(reminder_type)
        self.assertEqual(length, 160)

    def display_sms_length_for_a_reminder_type(self, all_reminder_page, reminder_type):
        reminder_settings = all_reminder_page.click_reminder_settings_tab()
        getattr(reminder_settings, "enable_%s_deadline_reminder" % reminder_type)()
        getattr(reminder_settings, "set_message_for_%s_deadline_reminder" % reminder_type)("1234567890")
        length = reminder_settings.get_sms_text_length_for_a_reminder_type(reminder_type)
        self.assertEqual(length, 10)

    @attr("functional_test")
    def test_deadline_type_should_remain_after_saving(self):
        all_reminder_page = self.go_to_reminder_page(fetch_(PROJECT_NAME, from_(DEADLINE_FIRST_DAY_OF_SAME_MONTH)), VALID_CREDENTIALS)
        reminder_settings = all_reminder_page.click_reminder_settings_tab()
        reminder_settings = all_reminder_page.set_deadline_by_week(reminder_settings, fetch_(DEADLINE, from_(DEADLINE_SECOND_DAY_OF_FOLLOWING_WEEK)))
        text_example_before_save = reminder_settings.get_example_text()
        reminder_settings.save_reminders()
        self.assertEqual(reminder_settings.get_example_text(), text_example_before_save)



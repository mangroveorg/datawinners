
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from pages.resetpasswordpage.reset_password_page import ResetPasswordPage
from tests.activateaccounttests.activate_account_data import DS_ACTIVATION_URL, DS_ACTIVATION_UID_N_TOKEN, NEW_PASSWORD
from testdata.test_data import url


@attr('suit_1')
class TestActivateDSAccount(BaseTest):
    def setUp(self):
        super(TestActivateDSAccount, self).setUp()

    def tearDown(self):
        super(TestActivateDSAccount, self).tearDown()


    @attr('functional_test')
    def test_activate_datasender_account(self):
        self.driver.go_to(url(DS_ACTIVATION_URL % DS_ACTIVATION_UID_N_TOKEN))
        activation_page = ResetPasswordPage(self.driver)
        activation_page.type_same_password(NEW_PASSWORD)
        activation_page.click_submit()
        self.assertEqual(self.driver.get_title(), "Data Submission")
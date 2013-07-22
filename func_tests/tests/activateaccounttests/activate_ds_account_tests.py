
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.http import int_to_base36

from framework.base_test import BaseTest
from pages.resetpasswordpage.reset_password_page import ResetPasswordPage
from tests.activateaccounttests.activate_account_data import DS_ACTIVATION_URL, NEW_PASSWORD
from testdata.test_data import url


@attr('suit_1')
class TestActivateDSAccount(BaseTest):

    @attr('functional_test')
    def test_activate_datasender_account(self):
        user = User.objects.get(pk=6)
        token = default_token_generator.make_token(user)
        self.driver.go_to(url(DS_ACTIVATION_URL % (int_to_base36(user.id),token)))
        activation_page = ResetPasswordPage(self.driver)
        activation_page.type_same_password(NEW_PASSWORD)
        activation_page.click_submit()
        self.assertEqual(self.driver.get_title(), "Data Submission")
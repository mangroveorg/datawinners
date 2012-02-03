# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from datawinners.accountmanagement.helper import get_trial_account_user_phone_numbers
from datawinners.tests.data import TRIAL_ACCOUNT_USERS_MOBILE_NUMBERS

class TestHelper(unittest.TestCase):
    def test_get_mobile_numbers_for_trial_account(self):
        self.assertEqual(TRIAL_ACCOUNT_USERS_MOBILE_NUMBERS,get_trial_account_user_phone_numbers())
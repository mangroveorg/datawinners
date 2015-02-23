# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.test import TestCase
from mock import Mock, patch, PropertyMock

from datawinners.accountmanagement.helper import get_trial_account_user_phone_numbers, get_all_users_for_organization
from datawinners.tests.data import TRIAL_ACCOUNT_USERS_MOBILE_NUMBERS


class TestHelper(TestCase):

    fixtures = ['test_data.json']

    def test_get_mobile_numbers_for_trial_account(self):
        self.assertSetEqual(set(TRIAL_ACCOUNT_USERS_MOBILE_NUMBERS),set(get_trial_account_user_phone_numbers()))

    def test_SMS_API_Users_not_shown_on_user_list_page(self):
        with patch('datawinners.accountmanagement.helper.User') as user_class:
            objects = Mock()
            type(user_class).objects = PropertyMock(return_value=objects)
            get_all_users_for_organization("SLX364903")
            objects.exclude.assert_called_once_with(groups__name__in=['Data Senders', 'SMS API Users'])


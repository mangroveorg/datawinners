# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest

from mock import patch
from datawinners.accountmanagement.forms import FullRegistrationForm


class TestFullRegistrationForm(unittest.TestCase):
    def test_email_is_converted_to_lower_case(self):
        uppercase_email_id = 'A@b.com'
        base_form = {'first_name': 'a',
                     'last_name': 'b',
                     'email': uppercase_email_id,
                     'password1': 'a', 'password2': 'a', 'organization_name': 'ad',
                     'organization_address': 'asa', 'organization_city': 'aaa', 'organization_country': 'aa',
                     'organization_zipcode': 'asd', 'organization_sector': 'Other', 'invoice_period':'pay_monthly'
        }

        form = FullRegistrationForm(base_form)
        with patch.object(FullRegistrationForm, 'clean_email') as get_clean_email:
            with patch.object(FullRegistrationForm, 'clean_username') as get_clean_username:
                get_clean_email.return_value = uppercase_email_id
                get_clean_username.return_value = None
                self.assertTrue(form.is_valid())
                self.assertTrue(form.cleaned_data.get('email') == 'a@b.com')

    def test_error_when_password_and_confirm_password_do_not_match(self):
        base_form = {'first_name': 'a',
                     'last_name': 'b',
                     'email': 'A@b.com',
                     'password1': 'a',
                     'password2': 'b',
                     'organization_name': 'ad',
                     'organization_addressline1': 'asa',
                     'organization_city': 'aaa',
                     'organization_country': 'aa',
                     'organization_zipcode': 'asd',
                     'organization_sector': 'Other',
                     'invoice_period':'pay_monthly'
        }
        form = FullRegistrationForm(base_form)
        with patch.object(FullRegistrationForm, 'clean_email') as get_clean_email:
            with patch.object(FullRegistrationForm, 'clean_username') as get_clean_username:
                get_clean_email.return_value = 'A@b.com'
                get_clean_username.return_value = None
                self.assertFalse(form.is_valid())
                self.assertTrue(form.errors['password1'])

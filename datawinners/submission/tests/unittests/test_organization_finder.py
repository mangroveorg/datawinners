# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from mock import Mock, patch
from nose.plugins.attrib import attr
from datawinners.accountmanagement.models import Organization, OrganizationSetting
from datawinners.submission.organization_finder import OrganizationFinder

#@attr('unit_test')
class TestOrganizationFinder(unittest.TestCase):

    @attr('unit_test')
    def test_should_find_organization_for_paid_account_using_any_of_multiple_registered_phone_numbers(self):
        mock_org = Mock(spec=Organization)
        mock_org.name  = 'Argha\'s TEST Organization'
        mock_org_setting = Mock(spec=OrganizationSetting)

        mock_org_setting.organization = mock_org
        mock_org_setting.sms_tel_number  = '3283298932,328,298,932'

        with patch.object(OrganizationFinder, "_find_organization_settings") as func_mock:
            func_mock.return_value = [mock_org_setting]

            org, error = OrganizationFinder().find_paid_organization('3283298932')
            self.assertIsNotNone(org)
            self.assertIsNone(error)
            self.assertEqual(org.name, 'Argha\'s TEST Organization')

    @attr('unit_test')
    def test_should_not_return_organization_for_partial_matches_on_phone_number(self):
        mock_org = Mock(spec=Organization)
        mock_org.name  = 'Argha\'s TEST Organization'
        mock_org_setting = Mock(spec=OrganizationSetting)

        mock_org_setting.organization = mock_org
        mock_org_setting.sms_tel_number  = '3283298932,328,298,932'

        with patch.object(OrganizationFinder, "_find_organization_settings") as func_mock:
            func_mock.return_value = [mock_org_setting]

            org, error = OrganizationFinder().find_paid_organization('32')
            self.assertIsNone(org)
            self.assertIsNotNone(error)
            self.assertEqual(error, 'No organization found for telephone number 32')

    def create_mock_org_and_org_setting(self, org_name, phone_numbers):
        mock_org = Mock(spec=Organization)
        mock_org.name = org_name
        mock_org_setting = Mock(spec=OrganizationSetting)
        mock_org_setting.organization = mock_org
        mock_org_setting.sms_tel_number = phone_numbers
        return mock_org, mock_org_setting

    @attr('unit_test')
    def test_should_return_organization_with_exact_match_on_phone_number(self):
        mock_org1, mock_org_setting1 = self.create_mock_org_and_org_setting(org_name = 'Argha\'s TEST Organization', phone_numbers = '3283298932,328,298,932')
        mock_org2, mock_org_setting2 = self.create_mock_org_and_org_setting(org_name = 'Ashish\'s TEST Organization', phone_numbers = '328329893,327,292')

        with patch.object(OrganizationFinder, "_find_organization_settings") as func_mock:
            func_mock.return_value = [mock_org_setting1, mock_org_setting2]

            org, error = OrganizationFinder().find_paid_organization('328329893')
            self.assertIsNotNone(org)
            self.assertIsNone(error)
            self.assertEqual(org.name, 'Ashish\'s TEST Organization')


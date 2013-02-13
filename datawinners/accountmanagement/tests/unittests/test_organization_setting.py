# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from mock import Mock, patch
from nose.plugins.attrib import attr
from datawinners.accountmanagement.models import Organization, OrganizationSetting

class TestOrganizationSetting(unittest.TestCase):

    @attr('unit_test')
    def test_should_get_organisation_sms_number(self):
        mock_org = Mock(spec=Organization)
        mock_org.in_trial_mode = False
        with patch.object(OrganizationSetting, "_get_organization") as func_mock:
            func_mock.return_value = mock_org
            numbers = OrganizationSetting(sms_tel_number='32323,4422').get_organisation_sms_number()
            self.assertEquals(['32323','4422'], numbers)

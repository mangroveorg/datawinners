from datetime import datetime

from django.test.client import RequestFactory
from django.utils import unittest
from mock import Mock

from datawinners.accountmanagement.decorators import is_not_expired
from datawinners.accountmanagement.models import Organization
from datawinners.accountmanagement.organization_id_creator import OrganizationIdCreator


class TestTrialAccount(unittest.TestCase):
    def create_organization(self, active_date=None):
        organization = Organization(name='twu',
                                    sector='Gaoxin',
                                    address='xian',
                                    city='Xian',
                                    state='ShanXi',
                                    country='CHN',
                                    zipcode='730000',
                                    office_phone='12345678911',
                                    website='http://google.com',
                                    active_date=active_date,
                                    org_id=OrganizationIdCreator().generateId()
        )
        organization.in_trial_mode=True
        return organization

    def test_organization_active_date_should_be_null_when_created(self):
        organization = self.create_organization()
        self.assertIsNone(organization.active_date)

    def test_organization_is_not_expired_when_activate_date_is_null(self):
        org = self.create_organization()
        self.assertFalse(org.is_expired())

    def setUp(self):
        self.org = self.create_organization(active_date=datetime(2011, 07, 1))
        self.org.save()

    def tearDown(self):
        self.org.delete()

    def test_organization_is_expired_when_more_than_3_months_has_passed(self):
        self.assertTrue(self.org.is_expired(current_time=datetime(2011, 11, 11)))

    def test_organization_is_not_expired_when_29_days_has_passed(self):
        self.assertFalse(self.org.is_expired(current_time=datetime(2011, 07, 30)))

    def test_organization_is_expired_when_30_days_has_passed(self):
        self.assertTrue(self.org.is_expired(current_time=datetime(2011, 07, 31)))

    def _initial_status_code_of(self, response):
        return response.status_code / 100

    def _prepare_request_with_user_of(self,org):
        request = RequestFactory().get('/dashboard/')
        request.user = Mock()
        mock_profile = Mock()
        mock_profile.org_id = Mock(return_value=org.org_id)
        request.user.get_profile = Mock(return_value=mock_profile)
        request.session = Mock()
        return request

    def test_is_expired_with_expired_trail_account_should_redirect(self):
        request = self._prepare_request_with_user_of(self.org)

        function = Mock()
        decorated_function=is_not_expired(function)

        response = decorated_function(request)
        self.assertEqual(self._initial_status_code_of(response),3)

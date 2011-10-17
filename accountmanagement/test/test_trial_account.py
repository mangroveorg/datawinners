from django.utils import unittest
from datawinners.accountmanagement.models import Organization
from datawinners.accountmanagement.organization_id_creator import OrganizationIdCreator
from datetime import datetime

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
        return organization

    def test_organization_active_date_should_be_null_when_created(self):
        organization = self.create_organization()
        self.assertIsNone(organization.active_date)

    def test_organization_is_not_expired_when_activate_date_is_null(self):
        org = self.create_organization()
        self.assertFalse(org.is_expired())

    def test_organization_is_expired_when_more_than_3_months_has_passed(self):
        org = self.create_organization(active_date=datetime(2011, 07, 11))
        self.assertTrue(org.is_expired(current_time=datetime(2011, 11, 11)))

    def test_organization_is_not_expired_when_29_days_has_passed(self):
        org = self.create_organization(active_date=datetime(2011, 07, 01))
        self.assertFalse(org.is_expired(current_time=datetime(2011, 07, 30)))

    def test_organization_is_expired_when_30_days_has_passed(self):
        org = self.create_organization(active_date=datetime(2011, 07, 01))
        self.assertTrue(org.is_expired(current_time=datetime(2011, 07, 31)))
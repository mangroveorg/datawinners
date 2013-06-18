# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from unittest.case import SkipTest
import couchdb
from django.test import Client
from django.conf import settings
from datawinners.accountmanagement.models import Organization, OrganizationSetting, TEST_REPORTER_MOBILE_NUMBER
from registration.models import RegistrationProfile
from django.contrib.auth.models import User
from datawinners.main.database import get_db_manager
from mangrove.transport.repository import reporters


@SkipTest
class TestMultiTenancy(unittest.TestCase):

    def test_should_create_organization_setting_with_document_store_on_create_organization(self):
        c = Client()
        reg_post = dict(
            email="arojis@gmail.com",
            first_name="first_name",
            last_name="last",
            organization_addressline1="x",
            organization_addressline2="y",
            organization_city="city",
            organization_country="country",
            organization_name="TEST_ORG_NAME",
            organization_office_phone="",
            organization_sector="PublicHealth",
            organization_state="state",
            organization_website="",
            organization_zipcode="zip",
            password1="a",
            password2="a",
            title="",
            )
        response = c.post('/register/', reg_post)
        self.assertIsNotNone(response)

        user = User.objects.get(email='arojis@gmail.com')
        profile = RegistrationProfile.objects.get(user=user)
        activation_key = profile.activation_key
        response = c.post('/activate/%s/' % activation_key)
        self.assertIsNotNone(response)

        organization = Organization.objects.get(name="TEST_ORG_NAME")
        organization_settings = OrganizationSetting.objects.get(organization=organization)
        organization_db_name = organization_settings.document_store

        expected_org_db_name = ("hni_test_org_name_%s" % (organization.org_id,)).lower()
        self.assertEqual(expected_org_db_name, organization_db_name)

        couch_server = couchdb.client.Server(settings.COUCH_DB_SERVER)
        couch_server.resource.credentials = settings.COUCHDB_CREDENTIALS

        org_db = None
        try:
            org_db = couch_server[organization_db_name]
        except Exception:
            self.fail("Organization database %s not created" % (organization_db_name,))
        self.assertIsNotNone(org_db)

        manager = get_db_manager(organization_db_name)
        test_reporter = reporters.find_reporter_entity(manager, TEST_REPORTER_MOBILE_NUMBER)
        self.assertIsNotNone(test_reporter)

        #clean up the org db
        del couch_server[organization_db_name]

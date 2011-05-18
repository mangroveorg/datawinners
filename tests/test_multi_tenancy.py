# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
import couchdb
import django
from django.db.backends.sqlite3.creation import DatabaseCreation
from django.test import Client
from django.test.utils import setup_test_environment, teardown_test_environment
from  datawinners import settings
from datawinners.accountmanagement.models import Organization, OrganizationSettings


class TestMultiTenancy(unittest.TestCase):
    def setUp(self):
        setup_test_environment()
        self.b = DatabaseCreation(django.db.connection)
        self.test_db = self.b.create_test_db(autoclobber=True)

    def tearDown(self):
        teardown_test_environment()
        self.b.destroy_test_db(self.test_db)

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
        response = c.post('/register', reg_post)
        self.assertIsNone(response)

        organization = Organization.objects.get(name="TEST_ORG_NAME")
        organization_settings = OrganizationSettings.objects.get(organization = organization)
        organization_db_name = organization_settings.document_store

        expected_org_db_name = ("hni_test_org_name_%s" % (organization.org_id,)).lower()
        self.assertEqual(expected_org_db_name,organization_db_name)

        couch_server = couchdb.client.Server(settings.COUCH_DB_SERVER)

        org_db = None
        try:
            org_db = couch_server[organization_db_name]
        except Exception:
            self.fail("Organization database %s not created" % (org_db,))
        self.assertIsNotNone(org_db)

        #clean up the org db
        del couch_server[organization_db_name]


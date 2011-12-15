from couchdb.client import Server
from django.core.management.base import BaseCommand
from datawinners import settings
from datawinners.accountmanagement.models import Organization, OrganizationSetting, NGOUserProfile
from mangrove.utils.types import is_empty

class Command(BaseCommand):
    args = '<org_id org_id ...>'


    def handle(self, *args, **options):
        if is_empty(args):
            print "give atleast one organization id. the command is python manage.py delete_org <id1 id2 ...>"

        for org_id in args:
            try:
                organization = Organization.objects.get(org_id=org_id)
                organization_setting = OrganizationSetting.objects.get(organization=organization)
                document_store = organization_setting.document_store
                self._delete_users_and_related_data(org_id)

                print "deleted organization users and related information for %s" %(org_id,)

                organization_setting.delete()
                organization.delete()

                print "deleted organization registration information for %s" %(org_id,)

                self._delete_couchdb_database(document_store)

                print "deleted submission, datarecords, form models for %s" %(org_id,)
                print "deleted organization complete for %s" %(org_id,)

            except Exception as e:
                print e
                print "error in deleting organization %s" %(org_id,)

    def _delete_couchdb_database(self, document_store):
        couchdb_server = Server(url=settings.COUCH_DB_SERVER)
        del couchdb_server[document_store]

    def _delete_users_and_related_data(self, org_id):
        user_profiles = NGOUserProfile.objects.filter(org_id=org_id)
        [user_profile.user.delete() for user_profile in user_profiles]



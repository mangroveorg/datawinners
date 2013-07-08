import logging
import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

from datawinners.accountmanagement.models import Organization, NGOUserProfile, OrganizationSetting
from datawinners.main.database import get_db_manager
from mangrove.datastore.datadict import get_or_create_data_dict
from mangrove.datastore.entity import create_entity
from mangrove.datastore.entity_type import entity_type_already_defined
from mangrove.datastore.queries import get_entity_count_for_type
from mangrove.errors.MangroveException import EntityTypeDoesNotExistsException
from mangrove.form_model.form_model import REPORTER, MOBILE_NUMBER_FIELD, NAME_FIELD
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE
from migration.couch.utils import init_migrations


init_migrations('/var/log/datawinners/dbs_migrated_release_7_0_0.csv')
logging.basicConfig(filename='/var/log/datawinners/migration_release_7_0_0.log', level=logging.DEBUG,
                    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


def _create_couchdb_datasender(manager, organization, current_user_name, mobile_number):
    total_entity = get_entity_count_for_type(manager, [REPORTER])
    reporter_short_code = 'rep' + str(total_entity + 1)
    entity = create_entity(dbm=manager, entity_type=REPORTER_ENTITY_TYPE, short_code=reporter_short_code,
                           location=[organization.country_name()])
    mobile_number_type = get_or_create_data_dict(manager, name='Mobile Number Type', slug='mobile_number',
                                                 primitive_type='string')
    name_type = get_or_create_data_dict(manager, name='Name', slug='name', primitive_type='string')
    data = [(MOBILE_NUMBER_FIELD, mobile_number, mobile_number_type), (NAME_FIELD, current_user_name, name_type)]
    entity.add_data(data=data)
    return reporter_short_code


def create_reporter_id_for_profile(dbm, org, profile):
    phone = profile.mobile_phone if profile.mobile_phone and profile.mobile_phone != "Not Assigned" else None
    if profile.reporter_id is None and entity_type_already_defined(dbm, REPORTER_ENTITY_TYPE):
        profile.reporter_id = _create_couchdb_datasender(dbm, org, profile.user.get_full_name(), phone)
        profile.save()


def process_all():
    for profile in NGOUserProfile.objects.filter(reporter_id=None):
        org = Organization.objects.get(org_id=profile.org_id)
        org_settings = OrganizationSetting.objects.get(organization=org)
        db_name = org_settings.document_store
        print "db " + db_name + " org:" + org.name
        try:
            manager = get_db_manager(db_name)
            create_reporter_id_for_profile(manager, org, profile)
        except EntityTypeDoesNotExistsException as e:
            print e.message


process_all()
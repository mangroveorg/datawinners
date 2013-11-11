import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

#noinspection PyUnresolvedReferences - used to initialize post save handlers for elasticsearch
from django.core.exceptions import ObjectDoesNotExist
from datawinners.accountmanagement.models import OrganizationSetting, get_ngo_admin_user_profiles_for
from mangrove.datastore.datadict import get_datadict_type_by_slug
from mangrove.datastore.entity import get_by_short_code_include_voided
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE
from datawinners.main.database import get_db_manager
from datawinners.main.couchdb.utils import all_db_names

import logging
from migration.couch.utils import migrate


def _add_location_field_if_absent(admin, dbm, logger):
    if "location" not in admin.data:
        logger.info('Adding location field to admin %s' % admin.short_code)
        data = ("location", admin.aggregation_paths["_geo"], get_datadict_type_by_slug(dbm, slug='location'))
        admin.update_latest_data([data])
    else:
        logger.info('Location field already present for admin %s' % admin.short_code)


def _get_admin_document(admin_profiles, dbm):
    admin_profile = admin_profiles[0]
    admin = get_by_short_code_include_voided(dbm, admin_profile.reporter_id, REPORTER_ENTITY_TYPE)
    return admin


def _get_admin_profiles(dbm):
    organization = OrganizationSetting.objects.get(document_store=dbm.database_name).organization
    admin_profiles = get_ngo_admin_user_profiles_for(organization)
    return admin_profiles


def migration_to_add_location_field_to_admins(db_name):
    logger = logging.getLogger(db_name)
    dbm = get_db_manager(db_name)
    try:
        logger.info('Migration started for database %s' % db_name)
        admin_profiles = _get_admin_profiles(dbm)
        if not admin_profiles or len(admin_profiles) == 0:
            logger.error('No admin for database %s' % db_name)
            return
        admin = _get_admin_document(admin_profiles, dbm)
        _add_location_field_if_absent(admin, dbm, logger)
    except ObjectDoesNotExist:
        logger.error("Entry not present for database: %s" % db_name)
    except Exception as e:
        logger.exception("Update of location failed for database: %s with exception: %s" % (db_name, e.message))


migrate(all_db_names(), migration_to_add_location_field_to_admins, version=(9, 0, 7))

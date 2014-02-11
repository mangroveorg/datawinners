import logging
from django.core.exceptions import ObjectDoesNotExist
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.entity.helper import delete_datasender_for_trial_mode
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate


map_voided_datasenders = """
function(doc) {
    if (doc.document_type == "Entity" && doc.aggregation_paths._type[0] == 'reporter' && doc.void) {
        emit(doc.short_code, null);
    }
}
"""

def _is_only_datasender(user):
    return user.groups.filter(name__in=["NGO Admins", "Project Managers"]).count() <= 0

def _delete_user_entry(dbm, user_profile, logger):
    profile_reporter_id = user_profile.reporter_id

    if profile_reporter_id.lower() == profile_reporter_id:
        logger.info("Not deleting user since the reporter id is already lowercase.")
    else:
        # user_profile.user.delete()
        logger.info("Deleting user with id: %s", profile_reporter_id)
        organization = Organization.objects.get(org_id=user_profile.org_id)
        if organization.in_trial_mode:
            logger.info("Deleting trail user with id: %s", profile_reporter_id)
            # delete_datasender_for_trial_mode(dbm, [profile_reporter_id.lower()], 'reporter')

def delete_voided_datasenders(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info('Starting migration')
        dbm = get_db_manager(db_name)
        for row in dbm.database.query(map_voided_datasenders):
            try:
                user_profiles = NGOUserProfile.objects.filter(reporter_id=row['key'])
                user = user_profiles[0].user
                if _is_only_datasender(user):
                    _delete_user_entry(dbm, user_profiles[0],logger)
            except IndexError:
                logger.info("User with reporter-id: '%s' does not exist" % row['key'])
    except Exception as e:
        logger.exception(e.message)


migrate(all_db_names(), delete_voided_datasenders, version=(10, 1, 4), threads=1)

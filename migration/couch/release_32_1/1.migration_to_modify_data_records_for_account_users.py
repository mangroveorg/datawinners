import logging
import time

from django.contrib.auth.models import User

from datawinners.accountmanagement.models import OrganizationSetting, NGOUserProfile
from datawinners.main.database import get_db_manager
from mangrove.datastore.entity import contact_by_short_code
from migration.couch.utils import migrate, mark_as_completed

logger = logging.getLogger("migration")

map_all_account_users = """
function(doc) {
    if (!doc.void && doc.document_type == "DataRecord" && doc.entity.document_type == "Contact" && doc.submission.form_code == null) {
        emit(doc.entity.short_code, null)
    }
}
"""


def _create_data_from_entity(reporter_entity):
    return [('name', reporter_entity.name), ("mobile_number", reporter_entity.data.get('mobile_number').get('value')),
            ('geo_code', reporter_entity.geometry.get('coordinates')),
            ('entity_type', reporter_entity.type_path),
            ('short_code', reporter_entity.short_code),
            ('location', reporter_entity.location_path),
            ('email', reporter_entity.email)]


def _void_existing_data_records(dbm, short_code):
    data_records = dbm.view.data_record_by_form_code(key=[None, short_code])
    for data_record in data_records:
        data_record_doc = data_record.value
        data_record_doc['void'] = True
        dbm.database.save(data_record_doc)


def recreate_data_records_for_account_users(database_name):
    try:
        start = time.time()
        organization_setting = OrganizationSetting.objects.get(document_store=database_name)
        org_id = organization_setting.organization_id
        account_user_ids = User.objects.filter(ngouserprofile__org_id=org_id,
                                               groups__name__in=["Project Managers", "Extended Users",
                                                                 "NGO Admins"]).values_list('id', flat=True)
        account_user_rep_ids = NGOUserProfile.objects.filter(user__id__in=account_user_ids).values_list('reporter_id',
                                                                                                        flat=True)
        dbm = get_db_manager(database_name)

        rows = dbm.database.query(map_all_account_users)
        rep_ids_for_migration = [row.key for row in rows if row.key in account_user_rep_ids]

        for rep_id in rep_ids_for_migration:
            reporter_entity = contact_by_short_code(dbm, rep_id)
            _void_existing_data_records(dbm, rep_id)
            reporter_entity.add_data(data=_create_data_from_entity(reporter_entity),
                                     submission={"form_code": "reg"})

        mark_as_completed(database_name)
        logger.info(
            'Time taken (seconds) for migrating {database_name} : {timetaken}'.format(database_name=database_name,
                                                                                      timetaken=(time.time() - start)))
    except Exception as e:
        logger.exception('Unexpected error while migrating data records for users', e.message)
        raise


logger.info('Started data record migration for user records')
start = time.time()
migrate(["hni_testorg_slx364903"], recreate_data_records_for_account_users, version=(32, 1, 0), threads=1)
logger.info('Completed data record migration for user records')
logger.info('Total Time taken (seconds) : {timetaken}'.format(timetaken=(time.time() - start)))

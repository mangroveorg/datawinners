from datawinners.accountmanagement.models import OrganizationSetting
from django.contrib.auth.models import User
from datawinners.main.database import get_db_manager
from mangrove.form_model.project import Project
from mangrove.datastore.documents import ProjectDocument
from datawinners.main.couchdb.utils import all_db_names
from migration.couch.utils import migrate, mark_as_completed
from datawinners.project.views.views import questionnaire
from mangrove.datastore.user_permission import UserPermission, update_user_permission
import traceback
import sys

map_all_questionnaire_id = """
function(doc) {
    if (doc.document_type == 'FormModel' && !doc.is_registration_model && doc.form_code != 'delete' && !doc.void) {
        emit(doc._id, null);
    }
}"""

def populate_user_permission(database_name):
    try:
        organization_setting = OrganizationSetting.objects.get(document_store=database_name)
        org_id = organization_setting.organization_id
        project_managers = User.objects.filter(ngouserprofile__org_id=org_id, groups__name__in=["Project Managers"])\
            .values_list('id', flat=True)
        dbm = get_db_manager(database_name)
        project_ids = [row.key for row in dbm.database.query(map_all_questionnaire_id)]
        for user_id in project_managers:
            update_user_permission(dbm, user_id, project_ids)
        mark_as_completed(database_name)
    except Exception as e:
        print 'Unexpected error while migrating user permission'
        print traceback.format_exc()
        raise
   	
migrate(all_db_names(), populate_user_permission, version=(26, 0, 2), threads=1)
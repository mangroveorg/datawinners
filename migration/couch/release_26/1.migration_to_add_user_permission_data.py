from datawinners.accountmanagement.models import OrganizationSetting
from django.contrib.auth.models import User
from datawinners.main.database import get_db_manager
from mangrove.form_model.project import Project
from mangrove.datastore.documents import ProjectDocument
from datawinners.main.couchdb.utils import all_db_names
from migration.couch.utils import migrate, mark_as_completed
from datawinners.project.views.views import questionnaire
from mangrove.datastore.user_permission import UserPermission

map_all_questionnaire_id = """
function(doc) {
    if (doc.document_type == 'FormModel' && !doc.void) {
        emit(doc._id, null);
    }
}"""

def populate_user_permission(database_name):
    organization_setting = OrganizationSetting.objects.get(document_store=database_name)
    org_id = organization_setting.organization_id
    ngo_admin = User.objects.filter(ngouserprofile__org_id=org_id, groups__name__in=["NGO Admins"])[0]
    project_managers = User.objects.filter(ngouserprofile__org_id=org_id, groups__name__in=["Project Managers"])\
        .values_list('id', flat=True)
    dbm = get_db_manager(database_name)
    project_ids = [row.key for row in dbm.database.query(map_all_questionnaire_id)]
    for user_id in project_managers:
        user_permission = UserPermission(dbm, user_id, project_ids)
        user_permission.save()
    mark_as_completed(database_name)	
   	
migrate(all_db_names(), populate_user_permission, version=(26, 0, 1), threads=1)
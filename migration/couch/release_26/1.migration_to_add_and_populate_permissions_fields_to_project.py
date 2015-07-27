from datawinners.accountmanagement.models import OrganizationSetting
from django.contrib.auth.models import User
from datawinners.main.database import get_db_manager
from mangrove.form_model.project import Project
from mangrove.datastore.documents import ProjectDocument
from datawinners.main.couchdb.utils import all_db_names
from migration.couch.utils import migrate, mark_as_completed


def add_and_populate_permission_fields(database_name):
    organization_setting = OrganizationSetting.objects.get(document_store=database_name)
    org_id = organization_setting.organization_id
    ngo_admin = User.objects.filter(ngouserprofile__org_id=org_id, groups__name__in=["NGO Admins"])[0]
    project_managers = User.objects.filter(ngouserprofile__org_id=org_id, groups__name__in=["Project Managers"])\
        .values_list('id', flat=True)

    dbm = get_db_manager(database_name)

    questionnaires = dbm.load_all_rows_in_view('all_projects')
    for row in questionnaires:
        doc = ProjectDocument.wrap(row['value'])
        questionnaire = Project.new_from_doc(dbm, doc)
        questionnaire._doc.creator = ngo_admin.id
        questionnaire.users_as_datasender = []
        questionnaire.users = project_managers
        questionnaire.save()
    mark_as_completed(database_name)

migrate(all_db_names(), add_and_populate_permission_fields, version=(26, 0, 1), threads=1)
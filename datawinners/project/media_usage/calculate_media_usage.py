from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.database import get_db_manager
from mangrove.form_model.project import Project


def calculate_usage(db_name, log_file_path):
    dbm = get_db_manager(db_name)
    rows = dbm.view.all_media_details(reduce=True)
    total_size_in_mb = rows[0][u"value"] if rows else 0
    if total_size_in_mb > 0:
        organization = OrganizationSetting.objects.get(document_store=db_name).organization
        text = "%s(%s) \nTotal used: %.2f mb\n" % (organization.name, organization.org_id, total_size_in_mb)
        usage_per_questionnaire = dbm.view.all_media_details(reduce=True, group=True)
        for row in usage_per_questionnaire:
            project = Project.get(dbm, row['key'])
            text += "%s (%s): Used: %.2f mb\n" % (project.name, project.id, row['value'])
        with open(log_file_path, "a") as log_file:
            log_file.write(text)

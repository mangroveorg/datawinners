from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.database import get_db_manager


def calculate_usage(db_name, log_file):
    dbm = get_db_manager(db_name)
    rows = dbm.view.media_attachment(reduce=True)
    total_size_in_mb = rows[0][u"value"] if rows else 0
    if total_size_in_mb > 0:
        organization = OrganizationSetting.objects.get(document_store=db_name).organization
        log_file.write("%s : %.2f mb" % (organization.org_id, total_size_in_mb))


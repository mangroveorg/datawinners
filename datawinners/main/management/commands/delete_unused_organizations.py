from django.core.management.base import BaseCommand
import xlrd
from datawinners.accountmanagement.models import Organization
from django.core import management
class Command(BaseCommand):
    def handle(self, *args, **options):
        import os
        import datawinners.settings as settings

        path = os.path.join(settings.PROJECT_DIR, 'main/management/commands/DW Account List - May 2012.xls')
        work_book = xlrd.open_workbook(path)
        work_sheet = work_book.sheets()[0]
        organization_names = work_sheet.col_values(0)
        org_id_set = set()
        for org_name in organization_names[59:179]:
            for org in Organization.objects.filter(name=org_name):
                if org.org_id not in ['MNV941502','SLX364903']:
                    org_id_set.add(org.org_id)
        for id in org_id_set:
            management.call_command('delete_org', id)
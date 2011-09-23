# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.http import HttpResponseRedirect
import xlwt
from datetime import datetime
from datawinners.accountmanagement.models import OrganizationSetting, Organization
from datawinners.main.utils import get_database_manager
from datawinners.project.models import get_all_projects
from mangrove.datastore.database import get_db_manager

def clean_date(date_val):
    new_date_val = date_val.replace(tzinfo=None)
    return new_date_val

def clean(row):
    new_row = []
    for each in row:
        if type(each) is datetime:
            each = clean_date(each)
        new_row.append(each)
    return new_row

def get_excel_sheet(raw_data, sheet_name):
    wb = xlwt.Workbook()
    ws = wb.add_sheet(sheet_name)
    for row_number, row  in enumerate(raw_data):
        row = clean(row)
        for col_number, val in enumerate(row):
            cell_style=xlwt.Style.default_style
            if isinstance(val, datetime):
                cell_style = xlwt.easyxf(num_format_str='dd-mm-yyyy hh:mm:ss')
            ws.write(row_number, col_number, val, style=cell_style)
    return wb

def is_new_user(f):
    def wrapper(*args, **kw):
        user = args[0].user
        if not len(get_all_projects(get_database_manager(args[0].user))) and not user.groups.filter(
            name="Data Senders").count() > 0:
            return HttpResponseRedirect("/start?page=" + args[0].path)

        return f(*args, **kw)

    return wrapper


def get_database_manager_for_org(organization):
    organization_settings = OrganizationSetting.objects.get(organization=organization)
    db = organization_settings.document_store
    return get_db_manager(database=db)

def get_organization(request):
    profile = request.user.get_profile()
    return Organization.objects.get(org_id=profile.org_id)

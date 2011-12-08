# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import xlwt
from datetime import datetime
from datawinners.accountmanagement.models import Organization
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




def get_database_manager_for_org(organization):
    return get_db_manager(database=organization.settings.document_store)

def get_organization(request):
    profile = request.user.get_profile()
    return Organization.objects.get(org_id=profile.org_id)

def convert_to_ordinal(number):
    if 10 < number < 14: return u'%sth' % number
    if number % 10 == 1: return u'%sst' % number
    if number % 10 == 2: return u'%snd' % number
    if number % 10 == 3: return u'%srd' % number
    return u'%sth' % number
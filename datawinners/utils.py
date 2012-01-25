# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.template.defaultfilters import slugify
import xlwt
from datetime import datetime
from mangrove.datastore.database import get_db_manager
from django.utils.translation import ugettext_lazy as _

VAR = "HNI"
def get_excel_sheet(raw_data, sheet_name):
    wb = xlwt.Workbook()
    workbook_add_sheet(wb, raw_data, sheet_name)
    return wb




def get_database_manager_for_org(organization):
    from datawinners.accountmanagement.models import OrganizationSetting

    organization_settings = OrganizationSetting.objects.get(organization=organization)
    db = organization_settings.document_store
    return get_db_manager(database=db)

def get_organization(request):
    from datawinners.accountmanagement.models import Organization

    profile = request.user.get_profile()
    return Organization.objects.get(org_id=profile.org_id)

def convert_to_ordinal(number):
    if 10 < number < 14: return _('%sth') % number
    if number % 10 == 1: return _('%sst') % number
    if number % 10 == 2: return _('%snd') % number
    if number % 10 == 3: return u'%srd' % number
    return _('%sth') % number

def generate_document_store_name(organization_name,organization_id):
    return slugify("%s_%s_%s" % (VAR, organization_name, organization_id))

def get_organization_settings_from_request(request):
    from datawinners.accountmanagement.models import OrganizationSetting
    return OrganizationSetting.objects.get(organization = get_organization(request))

def _clean_date(date_val):
    new_date_val = date_val.replace(tzinfo=None)
    return new_date_val

def _clean(row):
    new_row = []
    for each in row:
        if type(each) is datetime:
            each = _clean_date(each)
        new_row.append(each)
    return new_row

def workbook_add_sheet(wb, raw_data, sheet_name):
    ws = wb.add_sheet(sheet_name)
    for row_number, row  in enumerate(raw_data):
        row = _clean(row)
        for col_number, val in enumerate(row):
            cell_style=xlwt.Style.default_style
            if isinstance(val, datetime):
                cell_style = xlwt.easyxf(num_format_str='dd-mm-yyyy hh:mm:ss')
            ws.write(row_number, col_number, val, style=cell_style)
    return ws
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import re
from datetime import datetime

from django.template.defaultfilters import slugify
import xlwt
from django.utils.translation import ugettext_lazy as _, activate, get_language
from django.contrib.auth.forms import PasswordResetForm
from datawinners import settings
from datawinners.main.database import get_db_manager
from mangrove.form_model.field import ExcelDate
import unicodedata


VAR = "HNI"
SUBMISSION_DATE_QUESTION = u'Submission Date'
WIDTH_ONE_CHAR = 256
BUFFER_WIDTH = 2
MAX_ROWS_IN_MEMORY = 500
EXCEL_CELL_FLOAT_STYLE = xlwt.easyxf(num_format_str='#0.0###')
EXCEL_CELL_INTEGER_STYLE = xlwt.easyxf(num_format_str='#0')
EXCEL_DATE_STYLE = {'mm.yyyy': xlwt.easyxf(num_format_str='MMM, YYYY'),
                    'dd.mm.yyyy': xlwt.easyxf(num_format_str='MMM DD, YYYY'),
                    'mm.dd.yyyy': xlwt.easyxf(num_format_str='MMM DD, YYYY'),
                    'submission_date': xlwt.easyxf(num_format_str='MMM DD, YYYY hh:mm:ss')}

def get_excel_sheet(raw_data, sheet_name):
    wb = xlwt.Workbook()
    workbook_add_sheet(wb, raw_data, sheet_name)
    return wb


def sorted_unique_list(value_list):
    return sorted(list(set(value_list)))


def get_database_manager_for_org(organization):
    from datawinners.accountmanagement.models import OrganizationSetting

    organization_settings = OrganizationSetting.objects.get(organization=organization)
    return get_db_manager(organization_settings.document_store)


def get_organization(request):
    from datawinners.accountmanagement.models import Organization

    profile = request.user.get_profile()
    return Organization.objects.get(org_id=profile.org_id)


def get_organization_country(request):
    return get_organization(request).country_name()


def convert_to_ordinal(number):
    if 10 < number < 14: return _('%dth') % number
    if number % 10 == 1: return _('%dst') % number
    if number % 10 == 2: return _('%dnd') % number
    if number % 10 == 3: return _('%drd') % number
    return _('%dth') % number


def generate_document_store_name(organization_name, organization_id):
    return slugify("%s_%s_%s" % (VAR, organization_name, organization_id))


def get_organization_settings_from_request(request):
    from datawinners.accountmanagement.models import OrganizationSetting

    return OrganizationSetting.objects.get(organization=get_organization(request))


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


def _header_style():
    my_font = xlwt.Font()
    my_font.name = 'Helvetica Bold'
    my_font.bold = True
    my_alignment = xlwt.Alignment()
    my_alignment.vert = my_alignment.VERT_CENTER
    my_alignment.wrap = my_alignment.WRAP_AT_RIGHT
    header_style = xlwt.easyxf()
    header_style.font = my_font
    header_style.alignment = my_alignment
    return header_style


def workbook_add_sheet(wb, raw_data, sheet_name):
    ws = wb.add_sheet(sheet_name)

    for row_number, row in enumerate(raw_data):
        if(row_number == 0):
            row = _clean(row)
            style = xlwt.easyxf('borders: top double, bottom double, right double')
            algn = xlwt.Alignment()
            algn.wrap = 1
            style.alignment = algn

            for col_number, val in enumerate(row):
                if isinstance(val, tuple):
                    max_width = max([len(item) for item, style_object in val])
                    ws.col(col_number).width = WIDTH_ONE_CHAR * max_width
                    ws.row(row_number).height = WIDTH_ONE_CHAR * 5
                    ws.write_rich_text(row_number, col_number, val, style)
                else:
                    ws.row(row_number).height = WIDTH_ONE_CHAR * 4
                    ws.write(row_number, col_number, val, _header_style())

        else:
            if row_number > 0 and row_number % MAX_ROWS_IN_MEMORY == 0: ws.flush_row_data()
            row = _clean(row)
            write_row_to_worksheet(ws, row, row_number)
    return ws


def write_row_to_worksheet(ws, row, row_number):
    for col_number, val in enumerate(row):
        if isinstance(val, ExcelDate):
            ws.col(col_number).width = WIDTH_ONE_CHAR * (len(str(val.date)) + BUFFER_WIDTH)
            ws.write(row_number, col_number, val.date.replace(tzinfo=None),
                style=EXCEL_DATE_STYLE.get(val.date_format))
        elif isinstance(val, float):
            cell_format = EXCEL_CELL_FLOAT_STYLE
            if(int(val) == val):
                cell_format = EXCEL_CELL_INTEGER_STYLE
            ws.write(row_number, col_number, val, style=cell_format)
        else:
            ws.write(row_number, col_number, val, style=xlwt.Style.default_style)


def get_organization_from_manager(manager):
    from datawinners.accountmanagement.models import Organization, OrganizationSetting

    setting = OrganizationSetting.objects.get(document_store=manager.database_name)
    organization = Organization.objects.get(org_id=setting.organization_id)
    return organization


def send_reset_password_email(user, language_code):
    reset_form = PasswordResetForm({"email": user.email})
    if reset_form.is_valid():
        reset_form.save(email_template_name=_get_email_template_name_for_reset_password(language_code))


def _get_email_template_name_for_reset_password(language):
    return 'registration/password_reset_email_' + unicode(language) + '.html'


def convert_dmy_to_ymd(str_date):
    date = datetime.strptime(str_date, "%d-%m-%Y")
    return datetime.strftime(date, "%Y-%m-%d")


def get_changed_questions(olds, news, subject=True):
    i_old = 0
    deleted = []
    added = []
    changed = []
    changed_type = []
    if subject:
        if olds[-1].label != news[-1].label:
            changed.append(news[-1].label)
        olds = olds[:-1]
        news = news[:-1]
    for i_new, new in enumerate(news):
        while True:
            try:
                if new.name == olds[i_old].name:
                    if new.label != olds[i_old].label:
                        changed.append(new.label)
                    elif new.type != olds[i_old].type:
                        changed_type.append(dict({"label": new.label, "type": new.type}))
                    i_old += 1
                    break
                deleted.append(olds[i_old].label)
                i_old += 1
            except IndexError:
                added.append(new.label)
                break

    if i_old < len(olds):
        for key, old in enumerate(olds[i_old:]):
            deleted.append(old.label)

    all_type_dict = dict(changed=changed, changed_type=changed_type, added=added, deleted=deleted)
    return_dict = dict()
    for type, value in all_type_dict.items():
        if len(value):
            return_dict.update({type: value})
    return return_dict


def generate_project_name(project_names):
    default_name = _("Untitled Project")
    current_project = unicode(default_name)
    i = 1
    while current_project.lower() in project_names:
        current_project = u"%s - %d" % (default_name, i)
        i += 1
    return current_project


def _get_email_template_name_for_created_user(language):
    return 'registration/created_user_email_' + unicode(language) + '.html'

def translate(message, language="en", func=_):
    current_language = get_language()
    activate(language)
    translated = func(message)
    activate(current_language)
    return translated


def get_text_language_by_instruction(instruction):
    if re.match(r'^La r.ponse doit.+$', instruction):
        return "fr"
    return "en"

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def get_map_key(host):
    try:
        return settings.API_KEYS.get(host)
    except :
        return ""
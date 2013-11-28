from urllib import unquote
from django.http import HttpResponse
from django.template.defaultfilters import slugify
import xlwt
from datawinners.accountmanagement.decorators import valid_web_user
from datawinners.accountmanagement.helper import is_org_user
from datawinners.entity.entity_export_helper import get_subject_headers, get_submission_headers
from datawinners.entity.views import add_codes_sheet
from datawinners.main.database import get_database_manager
from datawinners.utils import get_excel_sheet
from mangrove.form_model.form_model import get_form_model_by_code, GEO_CODE_FIELD_NAME


def _get_submission_form_fields_for_user(form_model, request):
    form_fields = form_model.form_fields
    if form_model.entity_defaults_to_reporter():
        if not is_org_user(request.user):
            return filter(lambda field: field['code']!= form_model.entity_question.code, form_fields)
    return form_fields


@valid_web_user
def import_template(request, form_code):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_code(manager, form_code)
    if form_model.is_entity_registration_form():
        form_fields = form_model.form_fields
        headers = get_subject_headers(form_fields)
        field_codes = _field_codes(form_fields)
        sheet_name = request.GET["filename"]
    else:
        form_fields = _get_submission_form_fields_for_user(form_model, request)
        field_codes = _field_codes(form_fields)
        headers = get_submission_headers(form_fields)
        sheet_name = "Import_Submissions"

    filename = unquote(request.GET["filename"])
    workbook_response_factory = WorkBookResponseFactory(form_code, filename, sheet_name)
    return workbook_response_factory.create_workbook_response([headers], field_codes)


def _field_codes(fields):
    return [field['code'] for field in fields]

class WorkBookResponseFactory:
    def __init__(self, form_code, file_name, sheet_name):
        self.form_code = form_code
        self.file_name = file_name
        self.sheet_name = sheet_name

    def _add_styles(self, wb):
        ws = wb.get_sheet(0)
        style = xlwt.XFStyle()
        style.num_format_str = '@'
        for column in ws.get_cols().values():
            column.set_style(style)

    def create_workbook_response(self, data, field_codes):
        response = HttpResponse(mimetype='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="%s.xls"' % slugify(self.file_name)
        wb = get_excel_sheet(data, self.sheet_name)
        add_codes_sheet(wb, self.form_code, field_codes)
        self._add_styles(wb)
        wb.save(response)
        return response
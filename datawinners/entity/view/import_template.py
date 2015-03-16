from collections import OrderedDict
from urllib import unquote

import xlwt

from datawinners.accountmanagement.decorators import valid_web_user
from datawinners.accountmanagement.helper import is_org_user
from datawinners.entity.entity_export_helper import get_subject_headers, get_submission_headers
from datawinners.main.database import get_database_manager
from mangrove.form_model.form_model import get_form_model_by_code
from datawinners.project.submission.export import export_to_new_excel


@valid_web_user
def import_template(request, form_code):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_code(manager, form_code)
    filename = unquote(request.GET["filename"])
    if form_model.is_entity_registration_form():
        form_fields = form_model.form_fields
        headers = get_subject_headers(form_fields)
        field_codes = _field_codes(form_fields)
        sheet_name = request.GET["filename"]
    else:
        form_fields = form_model.form_fields
        field_codes = _field_codes(form_fields)
        headers = get_submission_headers(form_fields, form_model, is_org_user(request.user))
        sheet_name = "Import_Submissions"

    workbook_response_factory = WorkBookResponseFactory(form_code, filename, sheet_name,
                                                        browser=request.META.get('HTTP_USER_AGENT'),
                                                        is_entity_registration=form_model.is_entity_registration_form())
    return workbook_response_factory.create_workbook_response([headers], field_codes)


def _field_codes(fields):
    return [field['code'] for field in fields]

class WorkBookResponseFactory:
    def __init__(self, form_code, file_name, sheet_name, is_entity_registration=False, browser=None):
        self.form_code = form_code
        self.file_name = file_name
        self.sheet_name = sheet_name
        self.is_entity_registration = is_entity_registration
        self.browser = browser

    def _add_styles(self, wb):
        ws = wb.get_sheet(0)
        style = xlwt.XFStyle()
        style.num_format_str = '@'
        for column in ws.get_cols().values():
            column.set_style(style)

        ws.row(0).height = 256*7

    def create_workbook_response(self, data, field_codes):
        field_codes.insert(0, self.form_code)
        headers = OrderedDict()
        headers[self.sheet_name] = data[0]
        headers['codes'] = field_codes
        return export_to_new_excel(headers, {}, self.file_name, hide_codes_sheet=True, browser=self.browser)

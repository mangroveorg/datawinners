from django.http import HttpResponse
from project.ExcelHeader import ExcelFileSubmissionHeader, ExcelFileAnalysisHeader
from project.analysis import Analysis
from project.submission_list import SubmissionList
from project.submission_router import SubmissionRouter
from project.submission_utils.submission_formatter import SubmissionFormatter
from project.views import XLS_TUPLE_FORMAT
import helper
import datawinners.utils as utils


def export_submissions_in_xls_for_submission_log(request,form_model,manager):
    analyzer = _build_submission_list_for_submission_log_page_export(request, manager, form_model)
    formatted_values = SubmissionFormatter().get_formatted_values_for_list(analyzer.get_raw_values(), tuple_format=XLS_TUPLE_FORMAT)
    header_list = ExcelFileSubmissionHeader(form_model).header_list
    exported_data, file_name = _prepare_export_data(request, header_list, formatted_values)
    return _create_excel_response(exported_data, file_name)

def _build_submission_list_for_submission_log_page_export(request, manager, form_model):
    submission_type = request.GET.get('type')
    filters = request.POST
    keyword = request.POST.get('keyword', '')
    submission_list = SubmissionList(form_model, manager, helper.get_org_id_by_user(request.user), submission_type,
                                        filters,keyword)
    submission_list._init_excel_values()
    return submission_list

def export_submissions_in_xls_for_analysis_page(request,form_model,manager):
    analyzer = _build_submission_analyzer_for_analysis_export(request, manager, form_model)
    formatted_values = SubmissionFormatter().get_formatted_values_for_list(analyzer.get_raw_values(),
                                    tuple_format=XLS_TUPLE_FORMAT)
    header_list = ExcelFileAnalysisHeader(form_model).header_list
    exported_data, file_name = _prepare_export_data(request, header_list, formatted_values)
    return _create_excel_response(exported_data, file_name)

def _build_submission_analyzer_for_analysis_export(request, manager, form_model):
    #Analysis page wont hv any type since it has oly success submission data.
    filters = request.POST
    analysis = Analysis(form_model, manager, helper.get_org_id_by_user(request.user), filters)
    analysis._init_excel_values()
    return analysis

def _create_excel_response(raw_data_list, file_name):
    response = HttpResponse(mimetype="application/vnd.ms-excel")
    from django.template.defaultfilters import slugify

    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (slugify(file_name),)
    wb = utils.get_excel_sheet(raw_data_list, 'data_log')
    wb.save(response)
    return response


def _prepare_export_data(request, header_list, formatted_values):
    submission_log_type = request.GET.get('type', None)
    exported_data = _get_exported_data(header_list, formatted_values, submission_log_type)

    suffix = submission_log_type + '_log' if submission_log_type else 'analysis'
    project_name = request.POST.get(u"project_name")
    file_name = "%s_%s" % (project_name, suffix)
    return exported_data, file_name


def _get_exported_data(header, formatted_values, submission_log_type):
    data = [header] + formatted_values
    submission_id_col = 0
    status_col = 4
    reply_sms_col = 5
    if submission_log_type in [SubmissionRouter.ALL, SubmissionRouter.DELETED]:
        return [each[submission_id_col + 1:reply_sms_col] + each[reply_sms_col + 1:] for each in data]
    elif submission_log_type in [SubmissionRouter.ERROR]:
        return [each[submission_id_col + 1:status_col] + each[status_col + 1:] for each in data]
    elif submission_log_type in [SubmissionRouter.SUCCESS]:
        return [each[submission_id_col + 1:status_col] + each[reply_sms_col + 1:] for each in data]
    else:
        #for analysis page
        return [each[1:] for each in data]

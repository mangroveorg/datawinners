import json
import datetime
import logging
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext
from datawinners.accountmanagement.views import session_not_expired
from datawinners.custom_report_router.report_router import ReportRouter
from datawinners.utils import get_organization
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.submissions import Submission
from mangrove.utils.json_codecs import encode_json

from datawinners.accountmanagement.views import is_datasender
from datawinners.main.utils import get_database_manager
from datawinners.accountmanagement.views import is_not_expired
from project import helper
from project.ExcelHeader import  ExcelFileSubmissionHeader
from project.export_to_excel import _prepare_export_data, _create_excel_response
from project.submission_list import SubmissionList
from project.submission_list_for_excel import SubmissionListForExcel
from project.utils import    project_info
from project.Header import SubmissionsPageHeader
from project.analysis_result import AnalysisResult
from datawinners.activitylog.models import UserActivityLog
from datawinners.project.views.views import XLS_TUPLE_FORMAT
from datawinners.common.constant import   DELETED_DATA_SUBMISSION
from datawinners.project.submission_utils.submission_formatter import SubmissionFormatter

performance_logger = logging.getLogger("performance")

@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
# TODO : TW_BLR : delete_submissions should be a separate view with a redirect to this page
# TODO : TW_BLR : should have separate view for ui and data
def submissions(request, project_id=None, questionnaire_code=None):
    manager = get_database_manager(request.user)

    form_model = get_form_model_by_code(manager, questionnaire_code)
    submission_type = request.GET.get('type')
    filters = request.POST
    keyword = request.POST.get('keyword', '')
    org_id = helper.get_org_id_by_user(request.user)

    submissions = SubmissionList(form_model, manager, org_id, submission_type, filters, keyword)

    if request.method == 'GET':
        header = SubmissionsPageHeader(form_model)
        result_dict = {"header_list": header.header_list,
                       "header_name_list": repr(encode_json(header.header_list)),
                       "datasender_list": submissions.get_data_senders(),
                       "subject_list": submissions.get_subjects()
        }
        result_dict.update(project_info(request, manager, form_model, project_id, questionnaire_code))
        return render_to_response('project/results.html', result_dict, context_instance=RequestContext(request))

    if request.method == 'POST':
        field_values = SubmissionFormatter().get_formatted_values_for_list(submissions.get_raw_values())
        analysis_result = AnalysisResult(field_values, submissions.get_analysis_statistics(),
            submissions.get_data_senders(),submissions.get_subjects(), submissions.get_default_sort_order())
        performance_logger.info("Fetch %d submissions from couchdb." % len(analysis_result.field_values))

        if "id_list" in request.POST:
            project_infos = project_info(request, manager, form_model, project_id, questionnaire_code)
            return HttpResponse(_handle_delete_submissions(manager, request, project_infos.get("project").name))
        return HttpResponse(encode_json({'data_list': analysis_result.field_values,
                                         "statistics_result": analysis_result.statistics_result}))

def _handle_delete_submissions(manager, request, project_name):
    submission_ids = json.loads(request.POST.get('id_list'))
    received_times = delete_submissions_by_ids(manager, request, submission_ids)
    if len(received_times):
        UserActivityLog().log(request, action=DELETED_DATA_SUBMISSION, project=project_name,
            detail=json.dumps({"Date Received": "[%s]" % ", ".join(received_times)}))
        return encode_json({'success_message': ugettext("The selected records have been deleted"), 'success': True})
    return encode_json({'error_message': ugettext("No records deleted"), 'success': False})


def delete_submissions_by_ids(manager, request, submission_ids):
    received_times = []
    for submission_id in submission_ids:
        submission = Submission.get(manager, submission_id)
        received_times.append(datetime.datetime.strftime(submission.created, "%d/%m/%Y %X"))
        submission.void()
        if submission.data_record:
            ReportRouter().delete(get_organization(request).org_id, submission.form_code, submission.data_record.id)
    return received_times

@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
def export_log(request):
    project_name = request.POST.get(u"project_name")
    submission_type = request.GET.get('type')
    filters = request.POST
    keyword = request.POST.get('keyword', '')

    user = helper.get_org_id_by_user(request.user)
    manager = get_database_manager(request.user)
    questionnaire_code = request.POST.get('questionnaire_code')
    form_model = get_form_model_by_code(manager, questionnaire_code)

    submission_list = SubmissionListForExcel(form_model, manager, user, submission_type, filters, keyword)
    formatted_values = SubmissionFormatter().get_formatted_values_for_list(submission_list.get_raw_values(),
        tuple_format=XLS_TUPLE_FORMAT)
    header_list = ExcelFileSubmissionHeader(form_model).header_list
    exported_data, file_name = _prepare_export_data(submission_type, project_name, header_list, formatted_values)
    return _create_excel_response(exported_data, file_name)

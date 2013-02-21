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

import datawinners.utils as utils

from datawinners.accountmanagement.views import is_datasender
from datawinners.main.utils import get_database_manager, timebox
from datawinners.project.models import Project
from datawinners.accountmanagement.views import is_not_expired
import helper
from project import submission_analyser_helper, header_helper
from project.analysis import Analysis
from project.export_to_excel import export_submissions_in_xls_for_analysis_page, export_submissions_in_xls_for_submission_log
from project.submission_analyzer import SubmissionAnalyzer
from project.submission_router import successful_submissions
from project.submission_utils.submission_filter import SubmissionFilter
from project.utils import   make_project_links
from project.Header import SubmissionsPageHeader
from project.analysis_result import AnalysisResult
from datawinners.activitylog.models import UserActivityLog
from submission_list import SubmissionList
from datawinners.common.constant import   DELETED_DATA_SUBMISSION
from datawinners.project.submission_utils.submission_formatter import SubmissionFormatter

performance_logger = logging.getLogger("performance")

@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
# TODO : TW_BLR : delete_submissions should be a separate view with a redirect to this page
# TODO : TW_BLR : view should be renamed to submission logs
# TODO : TW_BLR : should have separate view for ui and data
def project_results(request, project_id=None, questionnaire_code=None):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_code(manager, questionnaire_code)
    analyzer = _build_submission_list_for_submission_log_page(request, manager, form_model)

    if request.method == 'GET':
        header = SubmissionsPageHeader(form_model)
        result_dict = {"header_list": header.header_list,
                       "header_name_list": repr(encode_json(header.header_list)),
                       "datasender_list": analyzer.get_data_senders(),
                       "subject_list": analyzer.get_subjects()
                       #                       "datasender_list": analysis_result.get_data_senders)
                       #                       "subject_id": analysis_result.get_subjects)
        }
        result_dict.update(project_info(request, manager, form_model, project_id, questionnaire_code))

        return render_to_response('project/results.html', result_dict, context_instance=RequestContext(request))
    if request.method == 'POST':
        field_values = SubmissionFormatter().get_formatted_values_for_list(analyzer.get_raw_values())
        analysis_result = AnalysisResult(field_values, analyzer.get_analysis_statistics(), analyzer.get_data_senders(), analyzer.get_subjects(), analyzer.get_default_sort_order())
        performance_logger.info("Fetch %d submissions from couchdb." % len(analysis_result.field_values))

        if "id_list" in request.POST:
            project_infos = project_info(request, manager, form_model, project_id, questionnaire_code)
            return HttpResponse(_handle_delete_submissions(manager, request, project_infos.get("project").name))
        return HttpResponse(encode_json({'data_list': analysis_result.field_values,
                                         "statistics_result": analysis_result.statistics_result}))

def _build_submission_list_for_submission_log_page(request, manager, form_model):
    submission_type = request.GET.get('type')
    filters = request.POST
    keyword = request.POST.get('keyword', '')
    submission_list = SubmissionList(form_model, manager, helper.get_org_id_by_user(request.user), submission_type, filters,
        keyword)
    submission_list._init_raw_values()
    return submission_list


def _build_submission_analyzer_for_analysis(request, manager, form_model):
    #Analysis page wont hv any type since it has oly success submission data.
    filters = request.POST
    analysis = Analysis(form_model, manager, helper.get_org_id_by_user(request.user), filters)
    analysis._init_raw_values()
    return analysis

def project_info(request, manager, form_model, project_id, questionnaire_code):
    project = Project.load(manager.database, project_id)
    is_summary_report = form_model.entity_defaults_to_reporter()
    rp_field = form_model.event_time_question
    in_trial_mode = _in_trial_mode(request)
    has_rp = rp_field is not None
    is_monthly_reporting = rp_field.date_format.find('dd') < 0 if has_rp else False

    return {"date_format": rp_field.date_format if has_rp else "dd.mm.yyyy",
            "is_monthly_reporting": is_monthly_reporting, "entity_type": form_model.entity_type[0].capitalize(),
            'project_links': (make_project_links(project, questionnaire_code)), 'project': project,
            'questionnaire_code': questionnaire_code, 'in_trial_mode': in_trial_mode,
            'reporting_period_question_text': rp_field.label if has_rp else None,
            'has_reporting_period': has_rp,
            'is_summary_report': is_summary_report}

def _in_trial_mode(request):
    return utils.get_organization(request).in_trial_mode

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
@timebox
def project_data(request, project_id=None, questionnaire_code=None):
    analysis_result = get_analysis_response(request, project_id, questionnaire_code)


    if request.method == "GET":
        return render_to_response('project/data_analysis.html',
            analysis_result,
            context_instance=RequestContext(request))

    elif request.method == "POST":
        return HttpResponse(analysis_result)

@timebox
def get_analysis_response(request, project_id, questionnaire_code):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_question_code(manager, questionnaire_code)
    filtered_submissions = filter_submissions(form_model, manager, request)
#    analysis_result = SubmissionAnalyzer(form_model, manager, helper.get_org_id_by_user(request.user),
#                                         filtered_submissions, request.POST.get('keyword', '')).analyse()
    analysis_result = Analysis(form_model, manager, helper.get_org_id_by_user(request.user),
                                         request.POST, request.POST.get('keyword', ''))
    analysis_result._init_raw_values()

    field_values = SubmissionFormatter().get_formatted_values_for_list(analysis_result.get_raw_values())
    temp_field_values = repr(encode_json(field_values))
#    performance_logger.info("Fetch %d submissions from couchdb." % len(analysis_result.field_values))
    performance_logger.info("Fetch %d submissions from couchdb." % len(temp_field_values))
    if request.method == 'GET':
        project_infos = project_info(request, manager, form_model, project_id, questionnaire_code)
        header_info = header_helper.header_info(form_model)

        analysis_dict = {
            "datasender_list" : analysis_result.get_data_senders(),
            "subject_list" : analysis_result.get_subjects(),
            "default_sort_order": repr(encode_json(analysis_result.get_default_sort_order())),
            "data_list": repr(encode_json(field_values)),
            "statistics_result": repr(encode_json(analysis_result.get_analysis_statistics()))
        }
#        analysis_result_dict = analysis_result.analysis_result_dict
        analysis_dict.update(project_infos)
        analysis_dict.update(header_info)
        return analysis_dict
#        return analysis_result_dict

    elif request.method == 'POST':
#        return encode_json(
#            {'data_list': analysis_result.field_values, "statistics_result": analysis_result.statistics_result})
        return encode_json(
            {
                "data_list": repr(encode_json(field_values)),
                "statistics_result": repr(encode_json(analysis_result.get_analysis_statistics()))
            }
        )

# TODO : Figure out how to mock mangrove methods
def get_form_model_by_question_code(manager, questionnaire_code):
    return get_form_model_by_code(manager, questionnaire_code)

def filter_submissions(form_model, manager, request):
    return SubmissionFilter(request.POST, form_model).filter(successful_submissions(manager, form_model.form_code))


def get_DB_manager_and_form_model(request):
    questionnaire_code = request.POST.get('questionnaire_code')
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_code(manager, questionnaire_code)
    return form_model, manager


@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
@timebox
#export_submissions_for_analysis
def export_data(request):
    project_name = request.POST.get(u"project_name")
    user = helper.get_org_id_by_user(request.user)
    filters = request.POST
    form_model, manager = get_DB_manager_and_form_model(request)
    return export_submissions_in_xls_for_analysis_page(filters,form_model,manager,user,project_name)

@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
def export_log(request):
    project_name = request.POST.get(u"project_name")
    user = helper.get_org_id_by_user(request.user)
    submission_type = request.GET.get('type')
    filters = request.POST
    keyword = request.POST.get('keyword', '')
    filter_list = [submission_type,filters,keyword]
    form_model, manager = get_DB_manager_and_form_model(request)
    return export_submissions_in_xls_for_submission_log(filter_list,form_model,manager,user,project_name)



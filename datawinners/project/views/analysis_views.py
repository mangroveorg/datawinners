import logging
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired
from datawinners.main.database import get_database_manager
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.utils.json_codecs import encode_json

from datawinners.main.utils import  timebox
from datawinners.project import header_helper, helper
from datawinners.project.ExcelHeader import ExcelFileAnalysisHeader
from datawinners.project.analysis import Analysis
from datawinners.project.analysis_for_excel import AnalysisForExcel
from datawinners.project.export_to_excel import _prepare_export_data, _create_excel_response
from datawinners.project.utils import    project_info
from datawinners.project.views.views import XLS_TUPLE_FORMAT
from datawinners.project.submission_utils.submission_formatter import SubmissionFormatter

performance_logger = logging.getLogger("performance")

@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
@timebox
def index(request, project_id=None, questionnaire_code=None):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_code(manager, questionnaire_code)

    filters = request.POST
    keyword = request.POST.get('keyword', '')
    analysis = Analysis(form_model, manager, helper.get_org_id_by_user(request.user), filters, keyword)
    analysis_result = analysis.analyse()
    performance_logger.info("Fetch %d submissions from couchdb." % len(analysis_result.field_values))

    if request.method == "GET":
        project_infos = project_info(request, manager, form_model, project_id, questionnaire_code)
        header_info = header_helper.header_info(form_model)
        analysis_result_dict = analysis_result.analysis_result_dict
        analysis_result_dict.update(project_infos)
        analysis_result_dict.update(header_info)

        return render_to_response('project/data_analysis.html',
            analysis_result_dict,
            context_instance=RequestContext(request))
    elif request.method == "POST":
        response = encode_json({'data_list': analysis_result.field_values, "statistics_result": analysis_result.statistics_result})
        return HttpResponse(response)


@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
@timebox
def export(request):
    project_name = request.POST.get(u"project_name")
    filters = request.POST
    keyword = request.POST.get('keyword', '')

    user = helper.get_org_id_by_user(request.user)
    manager = get_database_manager(request.user)

    questionnaire_code = request.POST.get('questionnaire_code')
    form_model = get_form_model_by_code(manager, questionnaire_code)

    submissions = AnalysisForExcel(form_model, manager, user, filters, keyword)
    formatted_values = SubmissionFormatter().get_formatted_values_for_list(submissions.get_raw_values(),
        tuple_format=XLS_TUPLE_FORMAT)
    header_list = ExcelFileAnalysisHeader(form_model).header_list
    exported_data, file_name = _prepare_export_data(None, project_name, header_list, formatted_values)
    return _create_excel_response(exported_data, file_name)

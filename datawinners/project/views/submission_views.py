from collections import OrderedDict
from copy import deepcopy
import json
import re
import datetime
import logging
from string import capitalize

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_view_exempt
import jsonpickle
from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired, valid_web_user

from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.feeds.database import get_feeds_database
from datawinners.feeds.mail_client import mail_feed_errors
from datawinners.main.database import get_database_manager
from datawinners.project.submission.exporter import SubmissionExporter
from datawinners.search.submission_query import SubmissionQuery
from mangrove.form_model.field import SelectField
from mangrove.transport.player.new_players import WebPlayerV2
from datawinners.alldata.helper import get_visibility_settings_for
from datawinners.custom_report_router.report_router import ReportRouter
from datawinners.utils import get_organization
from mangrove.form_model.form_model import get_form_model_by_code, FormModel
from mangrove.utils.json_codecs import encode_json
from datawinners.project import helper
from datawinners.project.data_sender_helper import get_data_sender
from datawinners.project.helper import SUBMISSION_DATE_FORMAT_FOR_SUBMISSION
from datawinners.project.models import Project

from datawinners.project.utils import project_info, is_quota_reached
from datawinners.project.Header import SubmissionsPageHeader
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import DELETED_DATA_SUBMISSION, EDITED_DATA_SUBMISSION
from datawinners.project.views.utils import get_form_context, get_project_details_dict_for_feed
from datawinners.project.submission_form import EditSubmissionForm
from mangrove.transport.repository.survey_responses import get_survey_response_by_id
from mangrove.transport.contract.survey_response import SurveyResponse


performance_logger = logging.getLogger("performance")
websubmission_logger = logging.getLogger("websubmission")


@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
def headers(request, form_code):
    manager = get_database_manager(request.user)
    submission_type = request.GET.get('type', 'all')
    form_model = get_form_model_by_code(manager, form_code)
    headers = SubmissionsPageHeader(form_model, submission_type).get_column_title()
    response = []
    for header in headers:
        response.append({"sTitle": header})
    return HttpResponse(encode_json(response))


@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
def index(request, project_id=None, questionnaire_code=None, tab=0):
    manager = get_database_manager(request.user)

    form_model = get_form_model_by_code(manager, questionnaire_code)
    filters = request.POST
    org_id = helper.get_org_id_by_user(request.user)

    if request.method == 'GET':
        result_dict = {
            #"datasender_list": survey_responses.get_data_senders(),
            #"subject_list": survey_responses.get_subjects(),
            "tab": tab,
            "is_quota_reached": is_quota_reached(request, org_id=org_id),
            #"active_tab": submission_type
        }
        result_dict.update(project_info(request, manager, form_model, project_id, questionnaire_code))
        return render_to_response('project/results.html', result_dict, context_instance=RequestContext(request))


def get_survey_response_ids_from_request(dbm, request, form_model):
    if request.POST.get('all_selected', "false") == "true":
        search_filters = json.loads(request.POST.get("search_filters"))
        submission_type = request.POST.get("submission_type")
        query_params = {'search_filters': search_filters}
        if submission_type.lower() != 'all':
            query_params.update({'filter': submission_type})

        submissions = SubmissionQuery(form_model, query_params).query(dbm.database_name)

        return [submission[0] for submission in submissions]
    return json.loads(request.POST.get('id_list'))


def delete(request, project_id):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, project_id)
    form_model = FormModel.get(dbm, project.qid)
    survey_response_ids = get_survey_response_ids_from_request(dbm, request, form_model)
    received_times = []
    for survey_response_id in survey_response_ids:
        survey_response = SurveyResponse.get(dbm, survey_response_id)
        received_times.append(datetime.datetime.strftime(survey_response.submitted_on, "%d/%m/%Y %X"))
        feeds_dbm = get_feeds_database(request.user)
        additional_feed_dictionary = get_project_details_dict_for_feed(project)
        delete_response = WebPlayerV2(dbm, feeds_dbm).delete_survey_response(survey_response,
                                                                             additional_feed_dictionary,
                                                                             websubmission_logger)
        mail_feed_errors(delete_response, dbm.database_name)
        if survey_response.data_record:
            ReportRouter().delete(get_organization(request).org_id, survey_response.form_code,
                                  survey_response.data_record.id)

    if len(received_times):
        UserActivityLog().log(request, action=DELETED_DATA_SUBMISSION, project=project.name,
                              detail=json.dumps({"Date Received": "[%s]" % ", ".join(received_times)}))
        response = encode_json({'success_message': ugettext("The selected records have been deleted"), 'success': True})
    else:
        response = encode_json({'error_message': ugettext("No records deleted"), 'success': False})

    return HttpResponse(response)


def build_static_info_context(manager, survey_response, ui_model=None):
    form_ui_model = OrderedDict() if ui_model is None else ui_model
    static_content = {'Data Sender': get_data_sender(manager, survey_response),
                      'Source': capitalize(
                          survey_response.channel) if survey_response.channel == 'web' else survey_response.channel.upper(),
                      'Submission Date': survey_response.submitted_on.strftime(SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)
    }

    form_ui_model.update({'static_content': static_content})
    form_ui_model.update({'is_edit': True})
    form_ui_model.update({'status': ugettext('Success') if survey_response.status else ugettext('Error')})
    return form_ui_model


def construct_request_dict(survey_response, questionnaire_form_model):
    result_dict = {}
    for field in questionnaire_form_model.fields:
        value = survey_response.values.get(field.code) if survey_response.values.get(
            field.code) else survey_response.values.get(field.code.lower())
        if isinstance(field, SelectField) and field.type == 'select':
            #check if select field answer is present in survey response
            value = re.findall(r'[1-9]?[a-z]', value) if value else value
        result_dict.update({field.code: value})
    result_dict.update({'form_code': questionnaire_form_model.form_code})
    return result_dict


@valid_web_user
def edit(request, project_id, survey_response_id, tab=0):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    questionnaire_form_model = FormModel.get(manager, project.qid)

    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)
    survey_response = get_survey_response_by_id(manager, survey_response_id)
    back_link = reverse(index,
                        kwargs={"project_id": project_id, "questionnaire_code": questionnaire_form_model.form_code,
                                "tab": tab})
    form_ui_model = build_static_info_context(manager, survey_response)
    form_ui_model.update({"back_link": back_link})
    if request.method == 'GET':
        form_initial_values = construct_request_dict(survey_response, questionnaire_form_model)
        survey_response_form = EditSubmissionForm(manager, project, questionnaire_form_model, form_initial_values)

        form_ui_model.update(get_form_context(questionnaire_form_model.form_code, project, survey_response_form,
                                              manager, hide_link_class, disable_link_class))
        form_ui_model.update({"redirect_url": ""})

        if not survey_response_form.is_valid():
            error_message = _("Please check your answers below for errors.")
            form_ui_model.update({'error_message': error_message})
        return render_to_response("project/web_questionnaire.html", form_ui_model,
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        original_survey_response = survey_response.copy()
        is_errored_before_edit = True if survey_response.errors != '' else False
        form_ui_model.update({"redirect_url": request.POST.get("redirect_url")})
        form_ui_model.update({"click_after_reload": request.POST.get("click_after_reload")})
        if request.POST.get("discard"):
            survey_response_form = EditSubmissionForm(manager, project, questionnaire_form_model,
                                                      survey_response.values)

            form_ui_model.update(get_form_context(questionnaire_form_model.form_code, project, survey_response_form,
                                                  manager, hide_link_class, disable_link_class))
            return render_to_response("project/web_questionnaire.html", form_ui_model,
                                      context_instance=RequestContext(request))
        else:
            survey_response_form = EditSubmissionForm(manager, project, questionnaire_form_model, request.POST)

        form_ui_model.update(get_form_context(questionnaire_form_model.form_code, project, survey_response_form,
                                              manager, hide_link_class, disable_link_class))
        if not survey_response_form.is_valid():
            error_message = _("Please check your answers below for errors.")
            form_ui_model.update({'error_message': error_message})
            return render_to_response("project/web_questionnaire.html", form_ui_model,
                                      context_instance=RequestContext(request))

        success_message = _("Your changes have been saved.")
        form_ui_model.update({'success_message': success_message})
        if len(survey_response_form.changed_data) or is_errored_before_edit:
            created_request = helper.create_request(survey_response_form, request.user.username)

            additional_feed_dictionary = get_project_details_dict_for_feed(project)
            user_profile = NGOUserProfile.objects.get(user=request.user)
            feeds_dbm = get_feeds_database(request.user)
            if questionnaire_form_model.entity_type == ["reporter"]:
                owner_id = request.POST["eid"]
            else:
                owner_id = None
            response = WebPlayerV2(manager, feeds_dbm, user_profile.reporter_id) \
                .edit_survey_response(created_request, survey_response, owner_id,
                                      additional_feed_dictionary, websubmission_logger)
            mail_feed_errors(response, manager.database_name)
            if response.success:
                build_static_info_context(manager, survey_response, form_ui_model)
                ReportRouter().route(get_organization(request).org_id, response)
                _update_static_info_block_status(form_ui_model, is_errored_before_edit)
                log_edit_action(original_survey_response, survey_response, request, project.name,
                                questionnaire_form_model)
                if request.POST.get("redirect_url"):
                    return HttpResponseRedirect(request.POST.get("redirect_url"))
            else:
                del form_ui_model["success_message"]
                survey_response_form._errors = helper.errors_to_list(response.errors, questionnaire_form_model.fields)
        return render_to_response("project/web_questionnaire.html", form_ui_model,
                                  context_instance=RequestContext(request))


def log_edit_action(old_survey_response, new_survey_response, request, project_name, form_model):
    differences = new_survey_response.differs_from(old_survey_response)
    diff_dict = {}
    changed_answers = deepcopy(differences.changed_answers)
    if differences.changed_answers:
        for key, value in differences.changed_answers.iteritems():
            question_field = form_model._get_field_by_code(key)
            question_label = question_field.label
            #replacing question code with actual question text
            changed_answers[question_label] = changed_answers.pop(key)
            #relace option with value for choice field
            if isinstance(question_field, SelectField):
                changed_answers[question_label] = get_option_value_for_field(value, question_field)

        diff_dict.update({'changed_answers': changed_answers})
    diff_dict.update({'received_on': differences.created.strftime(SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)})
    diff_dict.update({'status_changed': differences.status_changed})
    activity_log = UserActivityLog()
    activity_log.log(request, project=project_name, action=EDITED_DATA_SUBMISSION, detail=json.dumps(diff_dict))


def get_choice_list(diff_value, question_field):
    #TODO change the method name formatted_field_value_for_excel
    prev_choice_values = question_field.formatted_field_values_for_excel(diff_value)
    return prev_choice_values


def get_option_value_for_field(diff_value, question_field):
    prev_choice_values = get_choice_list(diff_value["old"], question_field)

    reslt_dict = {"old": ', '.join(prev_choice_values) if prev_choice_values else diff_value["old"],
                  "new": ', '.join(get_choice_list(diff_value["new"], question_field))}

    return reslt_dict


@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
def export(request):
    project_name = request.POST.get(u"project_name")
    submission_type = request.GET.get(u'type')
    search_filters = json.loads(request.POST.get('search_filters'))
    questionnaire_code = request.POST.get(u'questionnaire_code')
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_code(manager, questionnaire_code)

    query_params = {"search_filters": search_filters,
                    "start_result_number": 0,
                    "number_of_results": 50000,
                    "order": "",
                    "order_by": 0
    }
    if submission_type != "all":
        query_params.update({"filter": submission_type})

    return SubmissionExporter(form_model, project_name, request.user) \
        .create_excel_response(submission_type, query_params)


def _update_static_info_block_status(form_model_ui, is_errored_before_edit):
    if is_errored_before_edit:
        form_model_ui.update({'is_error_to_success': is_errored_before_edit})
        form_model_ui['status'] = ugettext('Success')


@csrf_view_exempt
@valid_web_user
def get_submissions(request, form_code):
    dbm = get_database_manager(request.user)
    form_model = get_form_model_by_code(dbm, form_code)
    search_parameters = {}
    search_parameters.update({"start_result_number": int(request.POST.get('iDisplayStart'))})
    search_parameters.update({"number_of_results": int(request.POST.get('iDisplayLength'))})
    search_parameters.update({"order_by": int(request.POST.get('iSortCol_0'))})
    search_parameters.update({"order": "-" if request.POST.get('sSortDir_0') == "desc" else ""})
    search_filters = json.loads(request.POST.get('search_filters'))
    search_parameters.update({"search_filters": search_filters})
    search_text = search_filters.get("search_text", '').lower()
    search_parameters.update({"search_text": search_text})
    filter_type = request.GET['type']
    if filter_type.lower() != 'all':
        search_parameters.update({"filter": filter_type})
    user = request.user
    query_count, search_count, submissions = SubmissionQuery(form_model, search_parameters).paginated_query(user,
                                                                                                            form_model.id)

    return HttpResponse(
        jsonpickle.encode(
            {
                'data': submissions,
                'iTotalDisplayRecords': query_count,
                'iDisplayStart': int(request.POST.get('iDisplayStart')),
                "iTotalRecords": search_count,
                'iDisplayLength': int(request.POST.get('iDisplayLength'))
            }, unpicklable=False), content_type='application/json')

from collections import OrderedDict
from copy import deepcopy
import json
import re
import datetime
import logging
from string import capitalize

from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_view_exempt
from elasticutils import F
import jsonpickle
import resource
from psycopg2._psycopg import Boolean

from datawinners import settings
from datawinners.accountmanagement.localized_time import get_country_time_delta, convert_utc_to_localized
from datawinners.blue.xform_submission_exporter import XFormSubmissionExporter
from datawinners.blue.view import SurveyWebXformQuestionnaireRequest
from datawinners.blue.xform_bridge import XFormSubmissionProcessor
from datawinners.project import helper
from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired, valid_web_user
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.common.authorization import is_data_sender
from datawinners.feeds.database import get_feeds_database
from datawinners.feeds.mail_client import mail_feed_errors
from datawinners.main.database import get_database_manager
from datawinners.monitor.carbon_pusher import send_to_carbon
from datawinners.monitor.metric_path import create_path
from datawinners.project.submission.exporter import SubmissionExporter
from datawinners.project.submission.submission_search import get_submissions_paginated, \
    get_all_submissions_ids_by_criteria, get_facets_for_choice_fields, get_submission_count, \
    get_submissions_without_user_filters_count
from datawinners.search.index_utils import es_questionnaire_field_name
from datawinners.search.submission_headers import HeaderFactory
from datawinners.search.submission_index import get_code_from_es_field_name
from datawinners.search.submission_query import SubmissionQueryResponseCreator
from mangrove.form_model.field import SelectField, DateField, UniqueIdField, FieldSet, DateTimeField
from mangrove.form_model.project import Project
from mangrove.transport.player.new_players import WebPlayerV2
from datawinners.alldata.helper import get_visibility_settings_for
from datawinners.custom_report_router.report_router import ReportRouter
from datawinners.utils import get_organization
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.utils.json_codecs import encode_json
from datawinners.project.data_sender_helper import get_data_sender
from datawinners.project.helper import SUBMISSION_DATE_FORMAT_FOR_SUBMISSION, is_project_exist
from datawinners.project.utils import project_info, is_quota_reached
from datawinners.project.Header import SubmissionsPageHeader
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import DELETED_DATA_SUBMISSION, EDITED_DATA_SUBMISSION
from datawinners.project.views.utils import get_form_context, get_project_details_dict_for_feed, \
    is_original_question_changed_from_choice_answer_type, is_original_field_and_latest_field_of_type_choice_answer, \
    convert_choice_options_to_options_text, filter_submission_choice_options_based_on_current_answer_choices
from datawinners.project.submission_form import SurveyResponseForm
from mangrove.transport.repository.survey_responses import get_survey_response_by_id
from mangrove.transport.contract.survey_response import SurveyResponse


websubmission_logger = logging.getLogger("websubmission")
logger = logging.getLogger("datawinners")


@login_required
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
        response.append({"sTitle": ugettext(header)})
    return HttpResponse(encode_json(response))


def _get_date_fields_info(questionnaire):
    date_fields_array = []
    for date_field in questionnaire.date_fields:
        date_fields_array.append({
            'code': date_field.code,
            'label': date_field.label,
            'is_month_format': date_field.is_monthly_format,
            'format': date_field.date_format
        })
    return date_fields_array


def _is_unique_id_type_present(fields_array, unique_id_type):
    return len(
        [item for item in fields_array if item['type'] == 'unique_id' and item['entity_type'] == unique_id_type]) > 0


def _field_code(field, parent_code):
    if parent_code:
        return parent_code + '----' + field.code
    return field.code


def get_filterable_field_details(field, filterable_fields, parent_code):
    if isinstance(field, DateField):
        return {
            'type': 'date',
            'code': _field_code(field, parent_code),
            'label': field.label,
            'is_month_format': field.is_monthly_format,
            'format': field.date_format
        }
    elif isinstance(field, DateTimeField):
        return {
            'type': 'date',
            'code': _field_code(field, parent_code),
            'label': field.label,
            'is_month_format': field.is_monthly_format,
            'format': 'dd.mm.yyyy'
        }
    elif isinstance(field, UniqueIdField):
        if not _is_unique_id_type_present(filterable_fields, field.unique_id_type):
            return {
                'type': 'unique_id',
                'code': _field_code(field, parent_code),
                'entity_type': field.unique_id_type,
            }


def get_filterable_fields(fields, parent_code=None):
    filterable_fields = []
    for field in fields:
        field_detials = get_filterable_field_details(field, filterable_fields, parent_code)
        if field_detials:
            filterable_fields.append(field_detials)
        if isinstance(field, FieldSet) and field.is_group():
            filterable_fields.extend(get_filterable_fields(field.fields, field.code))
    return filterable_fields


@login_required
@session_not_expired
@is_datasender
@is_not_expired
@is_project_exist
def index(request, project_id=None, questionnaire_code=None, tab=0):
    manager = get_database_manager(request.user)
    org_id = helper.get_org_id_by_user(request.user)

    if request.method == 'GET':
        questionnaire = Project.get(manager, project_id)
        if questionnaire.is_void():
            dashboard_page = settings.HOME_PAGE + "?deleted=true"
            return HttpResponseRedirect(dashboard_page)

        filterable_fields = get_filterable_fields(questionnaire.fields)
        first_filterable_fields = filterable_fields.pop(0) if filterable_fields else None
        xform = questionnaire.xform
        result_dict = {
            "user_email": request.user.email,
            "tab": tab,
            "xform": xform,
            # first 3 columns are additional submission data fields (ds_is, ds_name and submission_status)
            "is_quota_reached": is_quota_reached(request, org_id=org_id),
            "first_filterable_field": first_filterable_fields,
            "filterable_fields": filterable_fields,
            "is_media_field_present": questionnaire.is_media_type_fields_present
        }

        result_dict.update(project_info(request, questionnaire, questionnaire_code))
        return render_to_response('project/submission_results.html', result_dict,
                                  context_instance=RequestContext(request))


def _is_account_with_large_submissions(dbm):
    return dbm.database_name == 'hni_usaid-mikolo_lei526034'


@login_required
@session_not_expired
@is_datasender
@is_not_expired
@is_project_exist
def analysis_results(request, project_id=None, questionnaire_code=None):
    manager = get_database_manager(request.user)
    org_id = helper.get_org_id_by_user(request.user)

    if request.method == 'GET':
        questionnaire = Project.get(manager, project_id)
        dashboard_page = settings.HOME_PAGE + "?deleted=true"
        if questionnaire.is_void():
            return HttpResponseRedirect(dashboard_page)

        filterable_fields = get_filterable_fields(questionnaire.fields)
        first_filterable_fields = filterable_fields.pop(0) if filterable_fields else None

        result_dict = {
            "xform": questionnaire.xform,
            "user_email": request.user.email,
            "is_quota_reached": is_quota_reached(request, org_id=org_id),
            "first_filterable_field": first_filterable_fields,
            "filterable_fields": filterable_fields,
            "is_media_field_present": questionnaire.is_media_type_fields_present
            # first 3 columns are additional submission data fields (ds_is, ds_name and submission_status
        }
        result_dict.update(project_info(request, questionnaire, questionnaire_code))
        return render_to_response('project/analysis_results.html', result_dict,
                                  context_instance=RequestContext(request))


def get_survey_response_ids_from_request(dbm, request, form_model, local_time_delta):
    if request.POST.get('all_selected', "false") == "true":
        search_filters = json.loads(request.POST.get("search_filters"))
        submission_type = request.POST.get("submission_type")
        search_parameters = {'filter': submission_type}
        search_parameters.update({'search_filters': search_filters})
        return get_all_submissions_ids_by_criteria(dbm, form_model, search_parameters, local_time_delta)
    return json.loads(request.POST.get('id_list'))


@is_project_exist
def delete(request, project_id):
    dbm = get_database_manager(request.user)
    questionnaire = Project.get(dbm, project_id)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)
    organization = get_organization(request)
    local_time_delta = get_country_time_delta(organization.country)
    survey_response_ids = get_survey_response_ids_from_request(dbm, request, questionnaire, local_time_delta)
    received_times = []
    for survey_response_id in survey_response_ids:
        survey_response = SurveyResponse.get(dbm, survey_response_id)
        received_times.append(
            datetime.datetime.strftime(convert_utc_to_localized(local_time_delta, survey_response.submitted_on),
                                       "%d/%m/%Y %X"))
        feeds_dbm = get_feeds_database(request.user)
        additional_feed_dictionary = get_project_details_dict_for_feed(questionnaire)
        delete_response = WebPlayerV2(dbm, feeds_dbm).delete_survey_response(survey_response,
                                                                             additional_feed_dictionary,
                                                                             websubmission_logger)
        mail_feed_errors(delete_response, dbm.database_name)
        if survey_response.data_record:
            ReportRouter().delete(get_organization(request).org_id, questionnaire.form_code,
                                  survey_response.data_record.id)

    if len(received_times):
        UserActivityLog().log(request, action=DELETED_DATA_SUBMISSION, project=questionnaire.name,
                              detail=json.dumps({"Date Received": "[%s]" % ", ".join(received_times)}))
        response = encode_json({'success_message': ugettext("The selected records have been deleted"), 'success': True})
    else:
        response = encode_json({'error_message': ugettext("No records deleted"), 'success': False})

    return HttpResponse(response)


def build_static_info_context(manager, survey_response, ui_model=None, questionnaire_form_model=None, reporter_id=None):
    form_ui_model = OrderedDict() if ui_model is None else ui_model
    sender_name, sender_id = get_data_sender(manager, survey_response)[:2]
    if sender_id == 'N/A':
        static_content = {'Data Sender': (survey_response.created_by, '')}
    else:
        static_content = {'Data Sender': (sender_name, sender_id)}
    static_content.update({'Source': capitalize(
        survey_response.channel) if survey_response.channel == 'web' else survey_response.channel.upper(),
                           'Submission Date': survey_response.submitted_on.strftime(
                               SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)})

    form_ui_model.update({'static_content': static_content})
    form_ui_model.update({'is_edit': True})
    form_ui_model.update({'status': ugettext('Success') if survey_response.status else ugettext('Error')})
    return form_ui_model


def construct_request_dict(survey_response, questionnaire_form_model, short_code):
    result_dict = {}
    for field in questionnaire_form_model.fields:
        value = survey_response.values.get(field.code) if survey_response.values.get(
            field.code) else survey_response.values.get(field.code.lower())
        original_field = questionnaire_form_model.get_field_by_code_and_rev(field.code,
                                                                            survey_response.form_model_revision)
        if is_original_question_changed_from_choice_answer_type(original_field, field):
            value = convert_choice_options_to_options_text(original_field, value)
        elif is_original_field_and_latest_field_of_type_choice_answer(original_field, field):
            value = filter_submission_choice_options_based_on_current_answer_choices(value, original_field, field)
        if isinstance(field, SelectField) and field.type == 'select':
            # check if select field answer is present in survey response
            value = re.findall(r'[1-9]?[a-z]', value) if value else value
        result_dict.update({field.code: value})
    result_dict.update({'form_code': questionnaire_form_model.form_code})
    result_dict.update({'dsid': short_code})
    return result_dict


@valid_web_user
def edit_xform_submission_get(request, project_id, survey_response_id):
    survey_request = SurveyWebXformQuestionnaireRequest(request, project_id, XFormSubmissionProcessor())
    if request.method == 'GET':
        return survey_request.response_for_xform_edit_get_request(survey_response_id)


@valid_web_user
@is_project_exist
def edit(request, project_id, survey_response_id, tab=0):
    manager = get_database_manager(request.user)
    questionnaire_form_model = Project.get(manager, project_id)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    reporter_id = NGOUserProfile.objects.get(user=request.user).reporter_id
    is_linked = reporter_id in questionnaire_form_model.data_senders
    reporter_name = NGOUserProfile.objects.get(user=request.user).user.first_name
    if questionnaire_form_model.is_void():
        return HttpResponseRedirect(dashboard_page)

    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)
    survey_response = get_survey_response_by_id(manager, survey_response_id)
    back_link = reverse(index,
                        kwargs={"project_id": project_id, "questionnaire_code": questionnaire_form_model.form_code,
                                "tab": tab})
    form_ui_model = build_static_info_context(manager, survey_response,
                                              questionnaire_form_model=questionnaire_form_model,
                                              reporter_id=reporter_id)
    form_ui_model.update({"back_link": back_link, 'is_datasender': is_data_sender(request)})
    data_sender = get_data_sender(manager, survey_response)
    short_code = data_sender[1]
    enable_datasender_edit = True if survey_response.owner_uid else False
    if request.method == 'GET':
        form_initial_values = construct_request_dict(survey_response, questionnaire_form_model, short_code)
        survey_response_form = SurveyResponseForm(questionnaire_form_model, form_initial_values,
                                                  datasender_name=data_sender[0], reporter_id=reporter_id,
                                                  reporter_name=reporter_name,
                                                  enable_datasender_edit=enable_datasender_edit)

        form_ui_model.update(get_form_context(questionnaire_form_model, survey_response_form, manager, hide_link_class,
                                              disable_link_class))
        form_ui_model.update({"redirect_url": "",
                              "reporter_id": reporter_id,
                              "is_linked": is_linked,
                              "reporter_name": reporter_name})

        if not survey_response_form.is_valid() or form_ui_model['datasender_error_message']:
            error_message = _("Please check your answers below for errors.")
            form_ui_model.update({'error_message': error_message,
                                  "reporter_id": reporter_id,
                                  "is_linked": is_linked,
                                  "reporter_name": reporter_name})
        return render_to_response("project/web_questionnaire.html", form_ui_model,
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        send_to_carbon(create_path('submissions.web.simple'), 1)
        original_survey_response = survey_response.copy()
        is_errored_before_edit = True if survey_response.errors != '' else False
        submitted_values = request.POST
        owner_id = submitted_values.get("dsid")
        form_ui_model.update({
            "redirect_url": submitted_values.get("redirect_url"),
            'is_datasender': is_data_sender(request)
        })
        form_ui_model.update({"click_after_reload": submitted_values.get("click_after_reload")})
        if submitted_values.get("discard"):
            survey_response_form = SurveyResponseForm(questionnaire_form_model, survey_response.values)

            form_ui_model.update(
                get_form_context(questionnaire_form_model, survey_response_form, manager, hide_link_class,
                                 disable_link_class))
            form_ui_model.update({
                "reporter_id": reporter_id,
                "is_linked": is_linked,
                "reporter_name": reporter_name})
            return render_to_response("project/web_questionnaire.html", form_ui_model,
                                      context_instance=RequestContext(request))
        else:
            form_initial_values = construct_request_dict(survey_response, questionnaire_form_model, short_code)
            if not owner_id:
                submitted_values = submitted_values.copy()
                submitted_values['dsid'] = form_initial_values['dsid']

            survey_response_form = SurveyResponseForm(questionnaire_form_model, submitted_values,
                                                      initial=form_initial_values,
                                                      enable_datasender_edit=enable_datasender_edit)

        form_ui_model.update(
            get_form_context(questionnaire_form_model, survey_response_form, manager, hide_link_class,
                             disable_link_class))
        form_ui_model.update({
            "reporter_id": reporter_id,
            "is_linked": is_linked})
        if not survey_response_form.is_valid():
            error_message = _("Please check your answers below for errors.")
            form_ui_model.update({'error_message': error_message,
                                  "reporter_id": reporter_id,
                                  "is_linked": is_linked})
            return render_to_response("project/web_questionnaire.html", form_ui_model,
                                      context_instance=RequestContext(request))

        success_message = _("Your changes have been saved.")
        form_ui_model.update({'success_message': success_message,
                              "reporter_id": reporter_id,
                              "is_linked": is_linked,
                              "reporter_name": reporter_name})
        # if len(survey_response_form.changed_data) or is_errored_before_edit:
        created_request = helper.create_request(survey_response_form, request.user.username)

        additional_feed_dictionary = get_project_details_dict_for_feed(questionnaire_form_model)
        user_profile = NGOUserProfile.objects.get(user=request.user)
        feeds_dbm = get_feeds_database(request.user)
        response = WebPlayerV2(manager, feeds_dbm, user_profile.reporter_id) \
            .edit_survey_response(created_request, survey_response, owner_id,
                                  additional_feed_dictionary, websubmission_logger)
        mail_feed_errors(response, manager.database_name)
        if response.success:
            build_static_info_context(manager, survey_response, form_ui_model, questionnaire_form_model, reporter_id)
            ReportRouter().route(get_organization(request).org_id, response)
            _update_static_info_block_status(form_ui_model, is_errored_before_edit)
            log_edit_action(original_survey_response, survey_response, request, questionnaire_form_model.name,
                            questionnaire_form_model)
            if submitted_values.get("redirect_url"):
                return HttpResponseRedirect(submitted_values.get("redirect_url"))
        else:
            del form_ui_model["success_message"]
            survey_response_form._errors = helper.errors_to_list(response.errors, questionnaire_form_model.fields)
            form_ui_model.update({
                "reporter_id": reporter_id,
                "is_linked": is_linked,
                "reporter_name": reporter_name})
        return render_to_response("project/web_questionnaire.html", form_ui_model,
                                  context_instance=RequestContext(request))


def log_edit_action(old_survey_response, new_survey_response, request, project_name, form_model):
    differences = new_survey_response.differs_from(old_survey_response)
    diff_dict = {}
    changed_answers = deepcopy(differences.changed_answers)
    if differences.changed_answers:
        for key, value in differences.changed_answers.iteritems():
            question_field = form_model.get_field_by_code(key)
            question_label = question_field.label
            # replacing question code with actual question text
            changed_answers[question_label] = changed_answers.pop(key)
            # relace option with value for choice field
            if isinstance(question_field, SelectField):
                changed_answers[question_label] = get_option_value_for_field(value, question_field)

        diff_dict.update({'changed_answers': changed_answers})
    diff_dict.update({'received_on': differences.created.strftime(SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)})
    diff_dict.update({'status_changed': differences.status_changed})
    activity_log = UserActivityLog()
    activity_log.log(request, project=project_name, action=EDITED_DATA_SUBMISSION, detail=json.dumps(diff_dict))


def formatted_field_value_for_excel(diff_value, question_field):
    prev_choice_values = question_field.formatted_field_values_for_excel(diff_value)
    return prev_choice_values


def get_option_value_for_field(diff_value, question_field):
    prev_choice_values = formatted_field_value_for_excel(diff_value["old"], question_field)

    reslt_dict = {"old": ', '.join(prev_choice_values) if prev_choice_values else diff_value["old"],
                  "new": ', '.join(formatted_field_value_for_excel(diff_value["new"], question_field))}

    return reslt_dict


@login_required
@session_not_expired
@is_datasender
@is_not_expired
def export_count(request):
    if request.method == 'GET':
        return HttpResponse(status=405)

    submission_type = request.GET.get(u'type')
    post_body = json.loads(request.POST['data'])
    search_filters = post_body['search_filters']
    questionnaire_code = post_body['questionnaire_code']
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_code(manager, questionnaire_code)
    organization = get_organization(request)
    local_time_delta = get_country_time_delta(organization.country)

    # the number_of_results limit will not be used for result-set size since scan-scroll api does not support it.
    #it is specified since the code-flow requires its value to be present

    query_params = {"search_filters": search_filters,
                    "start_result_number": 0,
                    "number_of_results": 4000,
                    "order": "",
                    "sort_field": "date"
    }

    search_text = search_filters.get("search_text", '')
    query_params.update({"search_text": search_text})
    query_params.update({"filter": submission_type})

    submission_count = get_submission_count(manager, form_model, query_params, local_time_delta)
    return HttpResponse(mimetype='application/json', content=json.dumps({"count": submission_count}))


def _advanced_questionnaire_export(current_language, form_model, is_media, local_time_delta, manager, project_name,
                                   query_params, submission_type):
    if not is_media:
        return XFormSubmissionExporter(form_model, project_name, manager, local_time_delta, current_language) \
            .create_excel_response(submission_type, query_params)

    else:
        return XFormSubmissionExporter(form_model, project_name, manager, local_time_delta, current_language) \
            .create_excel_response_with_media(submission_type, query_params)


def _create_export_artifact(form_model, manager, request, search_filters):
    # the number_of_results limit will not be used for result-set size since scan-scroll api does not support it.
    # it is specified since the code-flow requires its value to be present
    query_params = {"search_filters": search_filters,
                    "start_result_number": 0,
                    "number_of_results": 4000,
                    "order": "",
                    "sort_field": "date"
    }
    search_text = search_filters.get("search_text", '')
    submission_type = request.GET.get(u'type')
    query_params.update({"search_text": search_text})
    query_params.update({"filter": submission_type})
    is_media = False
    if request.POST.get('is_media') == u'true':
        is_media = True
    organization = get_organization(request)
    local_time_delta = get_country_time_delta(organization.country)
    project_name = request.POST.get(u"project_name")
    current_language = get_language()
    if form_model.xform:
        return _advanced_questionnaire_export(current_language, form_model, is_media, local_time_delta, manager,
                                              project_name, query_params, submission_type)

    return SubmissionExporter(form_model, project_name, manager, local_time_delta, current_language) \
        .create_excel_response(submission_type, query_params)


@login_required
@session_not_expired
@is_datasender
@is_not_expired
def export(request):
    if request.method == 'GET':  # To handle django error #3480
        return HttpResponse(status=405)

    search_filters = json.loads(request.POST.get('search_filters'))
    questionnaire_code = request.POST.get(u'questionnaire_code')
    manager = get_database_manager(request.user)

    form_model = get_form_model_by_code(manager, questionnaire_code)

    return _create_export_artifact(form_model, manager, request, search_filters)


def _update_static_info_block_status(form_model_ui, is_errored_before_edit):
    if is_errored_before_edit:
        form_model_ui.update({'is_error_to_success': is_errored_before_edit})
        form_model_ui['status'] = ugettext('Success')


def _get_field_to_sort_on(post_dict, form_model, filter_type):
    order_by = int(post_dict.get('iSortCol_0')) - 1
    header = HeaderFactory(form_model).create_header(filter_type)
    headers = header.get_field_names_as_header_name()
    meta_fields = ['ds_id', 'entity_short_code']
    for field in meta_fields:
        # Remove extra meta fields with which ordering in submission values
        # and submission headers will not match
        try:
            headers.remove(field)
        except ValueError:
            pass
    return headers[order_by]


@csrf_view_exempt
@valid_web_user
def get_submissions(request, form_code):
    dbm = get_database_manager(request.user)
    form_model = get_form_model_by_code(dbm, form_code)
    search_parameters = {}
    search_parameters.update({"start_result_number": int(request.POST.get('iDisplayStart'))})
    search_parameters.update({"number_of_results": int(request.POST.get('iDisplayLength'))})
    filter_type = request.GET['type']
    search_parameters.update({"filter": filter_type})

    search_parameters.update({"sort_field": _get_field_to_sort_on(request.POST, form_model, filter_type)})
    search_parameters.update({"order": "-" if request.POST.get('sSortDir_0') == "desc" else ""})
    search_filters = json.loads(request.POST.get('search_filters'))
    search_parameters.update({"search_filters": search_filters})
    search_text = search_filters.get("search_text", '')
    search_parameters.update({"search_text": search_text})
    organization = get_organization(request)
    local_time_delta = get_country_time_delta(organization.country)
    search_results, query_fields = get_submissions_paginated(dbm, form_model, search_parameters, local_time_delta)
    submission_count_with_filters = get_submission_count(dbm, form_model, search_parameters, local_time_delta)
    submission_count_without_filters = get_submissions_without_user_filters_count(dbm, form_model, search_parameters)
    submissions = SubmissionQueryResponseCreator(form_model, local_time_delta).create_response(query_fields,
                                                                                               search_results)

    return HttpResponse(
        jsonpickle.encode(
            {
                'data': submissions,
                'iTotalDisplayRecords': submission_count_with_filters,
                'iDisplayStart': int(request.POST.get('iDisplayStart')),
                "iTotalRecords": submission_count_without_filters,
                'iDisplayLength': int(request.POST.get('iDisplayLength'))
            }, unpicklable=False), content_type='application/json')


def get_facet_response_for_choice_fields(query_with_criteria, choice_fields, form_model_id):
    facet_results = []
    for field in choice_fields:
        field_name = es_questionnaire_field_name(field.code, form_model_id) + "_exact"
        facet_response = query_with_criteria.facet(field_name, filtered=True).facet_counts()
        facet_result_options = []
        facet_result = {
            "es_field_name": field_name,
            "facets": facet_result_options,
            # find total submissions containing specified answer
            "total": query_with_criteria.filter(~F(**{field_name: None})).count()
        }
        for option, facet_list in facet_response.iteritems():
            for facet in facet_list:
                facet_result_options.append({
                    "term": facet['term'],
                    "count": facet['count']
                })
            facet_results.append(facet_result)

    return facet_results


@csrf_view_exempt
@valid_web_user
def get_stats(request, form_code):
    dbm = get_database_manager(request.user)
    form_model = get_form_model_by_code(dbm, form_code)
    search_parameters = {}
    search_parameters.update({"start_result_number": 0})
    search_parameters.update({"number_of_results": 0})
    filter_type = "success"
    search_parameters.update({"filter": filter_type})

    search_parameters.update({"sort_field": "ds_id"})
    search_parameters.update({"order": "-" if request.POST.get('sSortDir_0') == "desc" else ""})
    search_filters = json.loads(request.POST.get('search_filters'))
    search_parameters.update({"search_filters": search_filters})
    search_text = search_filters.get("search_text", '')
    search_parameters.update({"search_text": search_text})
    organization = get_organization(request)
    local_time_delta = get_country_time_delta(organization.country)
    # total success submission count irrespective of current fields being present or not
    facet_results, total_submissions = get_facets_for_choice_fields(dbm, form_model, search_parameters,
                                                                    local_time_delta)

    return HttpResponse(json.dumps(
        {'result': create_statistics_response(facet_results, form_model),
         'total': total_submissions
        }), content_type='application/json')


def create_statistics_response(facet_results, form_model):
    analysis_response = OrderedDict()
    for facet_result in facet_results:
        field_code = get_code_from_es_field_name(facet_result['es_field_name'], form_model.id)
        field = form_model.get_field_by_code(field_code)

        field_options = [option['text'] for option in field.options]
        facet_result_options = []
        facet_terms = []
        for facet in facet_result['facets']:
            facet_result_options.append({'term': facet['term'], 'count': facet['count']})
            facet_terms.append(facet['term'])

        for option in field_options:
            if option not in facet_terms:
                facet_result_options.append({'term': option, 'count': 0})

        analysis_response.update({field.label: {
            'data': facet_result_options,
            'field_type': field.type,
            'count': facet_result['total']
        }
        })
    return analysis_response

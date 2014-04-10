from collections import OrderedDict
from copy import deepcopy
import json
import re
import datetime
import logging
from string import capitalize, lower

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_view_exempt
from elasticutils import F
import jsonpickle
from mangrove.datastore.entity import Entity
from mangrove.errors.MangroveException import FormModelDoesNotExistsException
from datawinners import settings
from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired, valid_web_user

from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.feeds.database import get_feeds_database
from datawinners.feeds.mail_client import mail_feed_errors
from datawinners.main.database import get_database_manager
from datawinners.project.submission.exporter import SubmissionExporter
from datawinners.search.index_utils import es_field_name
from datawinners.search.submission_headers import HeaderFactory
from datawinners.search.submission_index import get_code_from_es_field_name
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
from datawinners.project.submission_form import SurveyResponseForm
from mangrove.transport.repository.survey_responses import get_survey_response_by_id
from mangrove.transport.contract.survey_response import SurveyResponse


performance_logger = logging.getLogger("performance")
websubmission_logger = logging.getLogger("websubmission")


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


@login_required
@session_not_expired
@is_datasender
@is_not_expired
def index(request, project_id=None, questionnaire_code=None, tab=0):
    manager = get_database_manager(request.user)
    org_id = helper.get_org_id_by_user(request.user)

    if request.method == 'GET':
        questionnaire = Project.get(manager,project_id)
        if questionnaire.is_void():
            dashboard_page = settings.HOME_PAGE + "?deleted=true"
            return HttpResponseRedirect(dashboard_page)

        date_fields_array = []
        for date_field in questionnaire.date_fields:
            date_fields_array.append({
                'code': date_field.code,
                'label': date_field.label,
                'is_month_format': date_field.is_monthly_format
            })

        result_dict = {
            "tab": tab,
            "is_quota_reached": is_quota_reached(request, org_id=org_id),
            "date_fields": date_fields_array
            }
        result_dict.update(project_info(request, questionnaire, questionnaire_code))
        return render_to_response('project/submission_results.html', result_dict,
                                  context_instance=RequestContext(request))


@login_required
@session_not_expired
@is_datasender
@is_not_expired
def analysis_results(request, project_id=None, questionnaire_code=None):
    manager = get_database_manager(request.user)


    org_id = helper.get_org_id_by_user(request.user)

    if request.method == 'GET':
        questionnaire = Project.get(manager, project_id)
        dashboard_page = settings.HOME_PAGE + "?deleted=true"
        if questionnaire.is_void():
            return HttpResponseRedirect(dashboard_page)

        result_dict = {
            "is_quota_reached": is_quota_reached(request, org_id=org_id),
            }
        result_dict.update(project_info(request, questionnaire, questionnaire_code))
        return render_to_response('project/analysis_results.html', result_dict,
                                  context_instance=RequestContext(request))


def get_survey_response_ids_from_request(dbm, request, form_model):
    if request.POST.get('all_selected', "false") == "true":
        search_filters = json.loads(request.POST.get("search_filters"))
        submission_type = request.POST.get("submission_type")
        query_params = {'search_filters': search_filters}
        query_params.update({'filter': submission_type})

        submissions = SubmissionQuery(form_model, query_params).query(dbm.database_name)

        return [submission[0] for submission in submissions]
    return json.loads(request.POST.get('id_list'))


def delete(request, project_id):
    dbm = get_database_manager(request.user)
    questionnaire = Project.get(dbm, project_id)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if questionnaire.is_void():
        return HttpResponseRedirect(dashboard_page)
    survey_response_ids = get_survey_response_ids_from_request(dbm, request, questionnaire)
    received_times = []
    for survey_response_id in survey_response_ids:
        survey_response = SurveyResponse.get(dbm, survey_response_id)
        received_times.append(datetime.datetime.strftime(survey_response.submitted_on, "%d/%m/%Y %X"))
        feeds_dbm = get_feeds_database(request.user)
        additional_feed_dictionary = get_project_details_dict_for_feed(questionnaire)
        delete_response = WebPlayerV2(dbm, feeds_dbm).delete_survey_response(survey_response,
                                                                             additional_feed_dictionary,
                                                                             websubmission_logger)
        mail_feed_errors(delete_response, dbm.database_name)
        if survey_response.data_record:
            ReportRouter().delete(get_organization(request).org_id, survey_response.form_code,
                                  survey_response.data_record.id)

    if len(received_times):
        UserActivityLog().log(request, action=DELETED_DATA_SUBMISSION, project=questionnaire.name,
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

def _convert_choice_options_to_options_text(field, answer):
    options = field.get_options_map()
    value_list = []
    for answer_value in list(answer):
        value_list.append(options[answer_value])
    return ",".join(value_list)

def _filter_submission_choice_options_based_on_current_answer_choices(answer, original_field, latest_field):
    original_value_list = list(answer)
    original_option_map = original_field.get_options_map()
    latest_option_map = latest_field.get_options_map()
    new_value_list = []
    for item in original_value_list:
        if original_option_map.get(item) == latest_option_map.get(item):
            new_value_list.append(item)
    return "".join(new_value_list)

def _is_original_question_changed_from_choice_answer_type(original_field, latest_field):
    return isinstance(original_field, SelectField) and not isinstance(latest_field, SelectField)

def _is_original_field_and_latest_field_of_type_choice_answer(original_field, latest_field):
    return isinstance(original_field, SelectField) and isinstance(latest_field, SelectField)

def construct_request_dict(survey_response, questionnaire_form_model, short_code):
    result_dict = {}
    for field in questionnaire_form_model.fields:
        value = survey_response.values.get(field.code) if survey_response.values.get(
            field.code) else survey_response.values.get(field.code.lower())
        original_field = questionnaire_form_model.get_field_by_code_and_rev(field.code, survey_response.form_model_revision)
        if _is_original_question_changed_from_choice_answer_type(original_field, field):
            value = _convert_choice_options_to_options_text(original_field, value)
        elif _is_original_field_and_latest_field_of_type_choice_answer(original_field, field):
            value = _filter_submission_choice_options_based_on_current_answer_choices(value, original_field, field)
        if isinstance(field, SelectField) and field.type == 'select':
            #check if select field answer is present in survey response
            value = re.findall(r'[1-9]?[a-z]', value) if value else value
        result_dict.update({field.code: value})
    result_dict.update({'form_code': questionnaire_form_model.form_code})
    result_dict.update({'dsid': short_code})
    return result_dict


@valid_web_user
def edit(request, project_id, survey_response_id, tab=0):
    manager = get_database_manager(request.user)
    questionnaire_form_model = Project.get(manager, project_id)
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if questionnaire_form_model.is_void():
        return HttpResponseRedirect(dashboard_page)

    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)
    survey_response = get_survey_response_by_id(manager, survey_response_id)
    back_link = reverse(index,
                        kwargs={"project_id": project_id, "questionnaire_code": questionnaire_form_model.form_code,
                                "tab": tab})
    form_ui_model = build_static_info_context(manager, survey_response)
    form_ui_model.update({"back_link": back_link})
    data_sender = get_data_sender(manager, survey_response)
    short_code = data_sender[1]
    if request.method == 'GET':
        form_initial_values = construct_request_dict(survey_response, questionnaire_form_model, short_code)
        survey_response_form = SurveyResponseForm(questionnaire_form_model, form_initial_values,
                                                  datasender_name=data_sender[0])

        form_ui_model.update(get_form_context(questionnaire_form_model, survey_response_form, manager, hide_link_class,
                                              disable_link_class))
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
            survey_response_form = SurveyResponseForm(questionnaire_form_model, survey_response.values)

            form_ui_model.update(
                get_form_context(questionnaire_form_model, survey_response_form, manager, hide_link_class, disable_link_class))
            return render_to_response("project/web_questionnaire.html", form_ui_model,
                                      context_instance=RequestContext(request))
        else:
            survey_response_form = SurveyResponseForm(questionnaire_form_model, request.POST)

        form_ui_model.update(
            get_form_context(questionnaire_form_model, survey_response_form, manager, hide_link_class, disable_link_class))
        if not survey_response_form.is_valid():
            error_message = _("Please check your answers below for errors.")
            form_ui_model.update({'error_message': error_message})
            return render_to_response("project/web_questionnaire.html", form_ui_model,
                                      context_instance=RequestContext(request))

        success_message = _("Your changes have been saved.")
        form_ui_model.update({'success_message': success_message})
        if len(survey_response_form.changed_data) or is_errored_before_edit:
            created_request = helper.create_request(survey_response_form, request.user.username)

            additional_feed_dictionary = get_project_details_dict_for_feed(questionnaire_form_model)
            user_profile = NGOUserProfile.objects.get(user=request.user)
            feeds_dbm = get_feeds_database(request.user)
            owner_id = request.POST.get("dsid")

            response = WebPlayerV2(manager, feeds_dbm, user_profile.reporter_id) \
                .edit_survey_response(created_request, survey_response, owner_id,
                                      additional_feed_dictionary, websubmission_logger)
            mail_feed_errors(response, manager.database_name)
            if response.success:
                build_static_info_context(manager, survey_response, form_ui_model)
                ReportRouter().route(get_organization(request).org_id, response)
                _update_static_info_block_status(form_ui_model, is_errored_before_edit)
                log_edit_action(original_survey_response, survey_response, request, questionnaire_form_model.name,
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
                    "sort_field": "date"
    }

    search_text = search_filters.get("search_text", '')
    query_params.update({"search_text": search_text})
    query_params.update({"filter": submission_type})

    return SubmissionExporter(form_model, project_name, request.user) \
        .create_excel_response(submission_type, query_params)


def _update_static_info_block_status(form_model_ui, is_errored_before_edit):
    if is_errored_before_edit:
        form_model_ui.update({'is_error_to_success': is_errored_before_edit})
        form_model_ui['status'] = ugettext('Success')


def _get_field_to_sort_on(post_dict, form_model, filter_type):
    order_by = int(post_dict.get('iSortCol_0')) - 1
    header = HeaderFactory(form_model).create_header(filter_type)
    headers = header.get_header_field_names()
    try:
        #Remove extra meta fields with which ordering in submission values
        #and submission headers will not match
        headers.remove('ds_id')
        headers.remove('entity_short_code')
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


def get_facet_response_for_choice_fields(query_with_criteria, choice_fields, form_model_id):
    facet_results = []
    for field in choice_fields:
        field_name = es_field_name(field.code, form_model_id) + "_exact"
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
    user = request.user

    entity_headers, paginated_query, query_with_criteria = SubmissionQuery(form_model,
                                                                           search_parameters).query_to_be_paginated(
        form_model.id, user)
    facet_results = get_facet_response_for_choice_fields(query_with_criteria, form_model.choice_fields, form_model.id)

    #total success submission count irrespective of current fields being present or not
    total_submissions = query_with_criteria.count()

    return HttpResponse(json.dumps(
        {'result': create_statistics_response(facet_results, form_model),
         'total': total_submissions
        }), content_type='application/json')


def create_statistics_response(facet_results, form_model):
    analysis_response = {}
    for facet_result in facet_results:
        field_code = get_code_from_es_field_name(facet_result['es_field_name'], form_model.id)
        field = form_model._get_field_by_code(field_code)

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

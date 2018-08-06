from __builtin__ import dict
from operator import itemgetter
import logging
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.http import urlquote
from django.utils.translation import ugettext as _, get_language
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_response_exempt, csrf_view_exempt
import jsonpickle

from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired, is_allowed_to_view_reports, \
    is_new_user, valid_web_user
from datawinners.accountmanagement.localized_time import get_country_time_delta, convert_utc_to_localized
from datawinners.common.urlextension import append_query_strings_to_url
from datawinners.dataextraction.helper import convert_to_json_response
from datawinners.alldata.helper import get_all_project_for_user, get_visibility_settings_for, get_page_heading, \
    get_reports_list
from datawinners.settings import CRS_ORG_ID
from datawinners.main.database import get_database_manager
from mangrove.datastore.entity import get_all_entities
from datawinners.submission.models import DatawinnerLog
from datawinners.utils import get_organization
from datawinners.project.utils import is_quota_reached
from mangrove.form_model.project import Project
from mangrove.datastore.documents import ProjectDocument
from collections import OrderedDict
from datawinners.project.submission.exporter import FailedSubmissionExporter
from django.utils.translation import ugettext


datawinners_logger = logging.getLogger("datawinners")

REPORTER_ENTITY_TYPE = u'reporter'


def get_alldata_project_links():
    project_links = {'projects_link': reverse(index),
                     'reports_link': reverse(reports),
                     'failed_submissions_link': reverse(failed_submissions)
                     }
    return project_links


def get_project_analysis_and_log_link(project_id, questionnaire_code):
    disabled = ""
    analysis = reverse("submission_analysis", args=[project_id, questionnaire_code])
    log = reverse("submissions", args=[project_id, questionnaire_code])
    return analysis, disabled, log


def get_project_info(manager, project):
    project_id = project['_id']
    questionnaire = Project.new_from_doc(manager, ProjectDocument.wrap(project))
    questionnaire_code = questionnaire.form_code

    analysis, disabled, log = get_project_analysis_and_log_link(project_id, questionnaire_code)

    web_submission_link = reverse("web_questionnaire", args=[project_id])

    web_submission_link_disabled = 'disable_link'
    if 'web' in project['devices']:
        web_submission_link_disabled = ""

    create_subjects_links = {}
    for entity_type in questionnaire.entity_type:
        create_subjects_links.update(
            {entity_type: append_query_strings_to_url(reverse("subject_questionnaire", args=[project_id, entity_type]),
                                                      web_view=True)})
    if questionnaire.is_poll:
        project_link = reverse("submissions", args=[project_id, questionnaire_code])
    else:
        project_link = reverse('project-overview', args=[project_id])

    project_info = dict(project_id=project_id,
                        name=project['name'],
                        qid=questionnaire_code,
                        created=project['created'],
                        is_advanced_questionnaire=bool(project.get('xform')),
                        link=project_link,
                        log=log, analysis=analysis, disabled=disabled,
                        web_submission_link=web_submission_link,
                        web_submission_link_disabled=web_submission_link_disabled,
                        create_subjects_link=create_subjects_links,
                        entity_type=questionnaire.entity_type,
                        encoded_name=urlquote(project['name']),
                        import_template_file_name=slugify(project['name']),
                        is_poll=bool(questionnaire.is_poll),
                        is_project_manager=project.get('is_project_manager',False))
    return project_info


def get_project_list(request):
    questionnaires = get_all_project_for_user(request.user)
    manager = get_database_manager(request.user)
    return [get_project_info(manager, questionnaire) for questionnaire in questionnaires]


def projects_index(request):
    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)
    page_heading = get_page_heading(request)

    return disable_link_class, hide_link_class, page_heading


def is_crs_admin(request):
    return get_organization(request).org_id == CRS_ORG_ID and not request.user.get_profile().reporter


def is_crs_user(request):
    return get_organization(request).org_id == CRS_ORG_ID

def _get_visibility_settings_for(user,project):
    if user.is_ngo_admin() or user.is_extended_user() or project.get('is_project_manager', False) is True:
        return "", ""
    if user.get_profile().reporter or project.get('is_project_manager', False) is False:
        return "disable_link_for_reporter", "none"
    return "", ""

def _construct_project_dict(user, local_time_delta, project):
    project_id = project['project_id']
    delete_links = reverse('delete_project', args=[project_id])
    disable_link_class, hide_link_class = _get_visibility_settings_for(user, project)
    
    return dict(delete_links=delete_links,
                name=project['name'],
                created=convert_utc_to_localized(local_time_delta, project['created']),
                qid=project['qid'],
                link=project['link'],
                web_submission_link_disabled=project['web_submission_link_disabled'],
                web_submission_link=project['web_submission_link'],
                analysis=project['analysis'],
                disabled=project['disabled'],
                log=project['log'],
                create_subjects_link=project['create_subjects_link'],
                entity_type=project['entity_type'],
                encoded_name=project['encoded_name'],
                import_template_file_name=project['import_template_file_name'],
                is_advanced_questionnaire=bool(project['is_advanced_questionnaire']),
                is_poll=project['is_poll'],
                disable_link_class=disable_link_class,
                hide_link_class=hide_link_class
                )


@login_required
@session_not_expired
@is_new_user
@is_not_expired
def index(request):
    organization = get_organization(request)
    page_heading = get_page_heading(request)
    hide_for_data_sender = 'none' if request.user.get_profile().reporter else ''
    rows = get_project_list(request)
    project_list = []
    smart_phone_instruction_link = reverse("smart_phone_instruction")
    local_time_delta = get_country_time_delta(organization.country)
    for project in rows:
        project_list.append(_construct_project_dict(request.user, local_time_delta, project))
    project_list.sort(key=itemgetter('name'))

    activation_success = request.GET.get('activation', False)

    error_messages = []
    if "associate" in request.GET.keys():
        error_messages = [
            _('You may have been dissociated from the project. Please contact your administrator for more details.')]
    if is_crs_admin(request):
        return render_to_response('alldata/index.html',
                                  {'projects': project_list, 'page_heading': page_heading,
                                   'is_crs_admin': True,
                                   'project_links': get_alldata_project_links(),
                                   'is_quota_reached': is_quota_reached(request),
                                   'error_messages': error_messages,
                                   'is_pro_sms': organization.is_pro_sms,
                                   'activation_success': activation_success,
                                   'hide_for_data_sender': hide_for_data_sender,
                                   'hide_link_class': hide_for_data_sender,
                                   'current_lang': get_language()},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('alldata/index.html',
                                  {'projects': project_list, 'page_heading': page_heading,
                                   'is_crs_admin': False,
                                   "smart_phone_instruction_link": smart_phone_instruction_link,
                                   'project_links': get_alldata_project_links(),
                                   'is_quota_reached': is_quota_reached(request),
                                   'error_messages': error_messages,
                                   'is_pro_sms': organization.is_pro_sms,
                                   'activation_success': activation_success,
                                   'hide_for_data_sender':hide_for_data_sender,
                                   'hide_link_class': hide_for_data_sender,
                                   'current_lang': get_language()},
                                  context_instance=RequestContext(request))


def _get_failed_entries(organization, display_start=0, display_length=25, sort_col=2, sort_dir='asc'):
    header_dict = OrderedDict([('from_number', 'Data Sender'), ('created_at', 'Submission Date'),('form_code', 'Questionnaire Code'), ('message' , 'SMS Text'), ('error', 'Error message') ])
    order = list(header_dict.keys())[sort_col-1]
    total = DatawinnerLog.objects.filter(organization=organization).count()
    i_start = display_start
    if display_length == 0:
        i_end =  total
    else:
        i_end = display_start + display_length
    if sort_dir=='desc':
        order = '-' + order
    org_logs = DatawinnerLog.objects.filter(organization=organization).order_by(order)[i_start:i_end]
#    import IPython
#    IPython.embed()
    local_time_delta = get_country_time_delta(organization.country)
    for entry in org_logs:
        entry.created_at = convert_utc_to_localized(local_time_delta, entry.created_at)

    org_logs_flat = org_logs.values_list('from_number','created_at','form_code','message','error')
    return total, list(org_logs_flat)

@csrf_view_exempt
@csrf_response_exempt
@login_required
@session_not_expired
@is_new_user
@is_not_expired
def failed_submissions_ajax(request):
    try:
        organization = get_organization(request)
        total_display_records, org_logs = _get_failed_entries(organization,int(request.POST.get('iDisplayStart')),int(request.POST.get('iDisplayLength')),int(request.POST.get('iSortCol_0')),request.POST.get('sSortDir_0'))
        return HttpResponse(
        jsonpickle.encode(
            {
                'data': list(org_logs),
                'iTotalDisplayRecords': total_display_records,
                'iDisplayStart': int(request.POST.get('iDisplayStart')),
                "iTotalRecords": org_logs.__len__(),
                'iDisplayLength': int(request.POST.get('iDisplayLength'))
            }, unpicklable=False), content_type='application/json')

    except Exception as e:
        datawinners_logger.error("All Failed Ajax failed")
        datawinners_logger.error(request.POST)
        datawinners_logger.exception(e)
        raise

@valid_web_user
def failed_submissions(request):
    disable_link_class, hide_link_class, page_heading = projects_index(request)
    header_dict = OrderedDict([('from_number', 'Data Sender'), ('created_at', 'Submission Date'),('form_code', 'Questionnaire Code'), ('message' , 'SMS Text'), ('error1', 'Error Message') ])
    organization = get_organization(request)

    

    return render_to_response('alldata/failed_submissions.html',
                              {'page_heading': page_heading,
                               'failedsubmissions_headers' : header_dict,
                               'disable_link_class': disable_link_class,
                               'hide_link_class': hide_link_class, 'is_crs_admin': is_crs_admin(request),
                               'project_links': get_alldata_project_links(),
                               'is_quota_reached': is_quota_reached(request, organization=organization)},
                              context_instance=RequestContext(request))

def _create_export_artifact(request):
    try:
        organization = get_organization(request)
        total_display_records, org_logs = _get_failed_entries(organization, display_start=0, display_length=0)
        columns = [ugettext('Data Sender'), ugettext('Submission Date'), ugettext('Questionnaire Code'),
                   ugettext('SMS Text'), ugettext('Error message')]
        filename = ugettext('Failed Submissions')

    except Exception as e:
        datawinners_logger.error("All Failed Ajax failed")
        datawinners_logger.error(request.POST)
        datawinners_logger.exception(e)
        raise

    return FailedSubmissionExporter(filename, columns, org_logs).create_excel_response()


@valid_web_user
def export(request):
    if request.method == 'GET':  # To handle django error #3480
        return HttpResponse(status=405)

    return _create_export_artifact(request)

@valid_web_user
def export_count(request):
    if request.method == 'GET':
        return HttpResponse(status=405)

    submission_count = 4000
    return HttpResponse(mimetype='application/json', content=json.dumps({"count": submission_count}))


@valid_web_user
@is_allowed_to_view_reports
def reports(request):
    report_list = get_reports_list(get_organization(request).org_id, request.session.get('django_language', 'en'))
    if not is_crs_user(request):
        raise Http404

    response = render_to_response('alldata/reports_page.html',
                                  {'reports': report_list, 'page_heading': "Questionnaires",
                                   'project_links': get_alldata_project_links(),
                                   'is_quota_reached': is_quota_reached(request),
                                   'is_crs_admin': True},
                                  context_instance=RequestContext(request))
    response.set_cookie('crs_session_id', request.COOKIES['sessionid'])

    return response


@valid_web_user
def smart_phone_instruction(request, project_id=None):
    language_code = request.LANGUAGE_CODE
    instruction_template = "alldata/smart_phone_instruction_" + language_code + ".html"

    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)
    project_links = {}
    if project_id:
        project_links['test_questionnaire_link'] = reverse("web_questionnaire", args=[project_id])
    context = {'back_to_project_link': reverse("alldata_index"),
               'project_links': project_links,
               "instruction_template": instruction_template,
               "disable_link_class": disable_link_class,
               "hide_link_class": hide_link_class}

    return render_to_response("alldata/smart_phone_instruction.html", context,
                              context_instance=RequestContext(request))


@valid_web_user
def get_entity_list_by_type(request, entity_type):
    entity_type_list = [entity_type]
    if entity_type is None:
        return []
    manager = get_database_manager(request.user)
    entities = get_all_entities(manager, entity_type_list)
    return convert_to_json_response([entity.short_code for entity in entities])

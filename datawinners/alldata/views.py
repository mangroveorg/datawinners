from __builtin__ import dict
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired, is_allowed_to_view_reports, is_new_user, valid_web_user
from datawinners.common.urlextension import append_query_strings_to_url
from datawinners.dataextraction.helper import convert_to_json_response
from datawinners.alldata.helper import get_all_project_for_user, get_visibility_settings_for, get_page_heading, get_reports_list
from datawinners.settings import CRS_ORG_ID
from datawinners.project.models import ProjectState, Project
from datawinners.main.database import get_database_manager
from mangrove.datastore.entity import get_all_entities
from mangrove.datastore.entity_type import get_all_entity_types
from mangrove.form_model.form_model import FormModel
from datawinners.submission.models import DatawinnerLog
from datawinners.utils import get_organization
from datawinners.project.utils import is_quota_reached
from datawinners.entity.views import create_subject
from django.http import Http404

REPORTER_ENTITY_TYPE = u'reporter'


def get_alldata_project_links():
    project_links = {'projects_link': reverse(index),
                     'reports_link': reverse(reports),
                     'failed_submissions_link': reverse(failed_submissions)
    }
    return project_links


def get_project_analysis_and_log_link(project, project_id, questionnaire_code):
    analysis = log = "#"
    disabled = "disable_link"
    if project.state != ProjectState.INACTIVE:
        disabled = ""
        analysis = reverse("project_data", args=[project_id, questionnaire_code])
        log = reverse("submissions", args=[project_id, questionnaire_code])
    return analysis, disabled, log


def get_project_info(manager, raw_project):
    project_id = raw_project['value']['_id']
    project = Project.load(manager.database, project_id)
    questionnaire = manager.get(project.qid, FormModel)
    questionnaire_code = questionnaire.form_code

    analysis, disabled, log = get_project_analysis_and_log_link(project, project_id, questionnaire_code)

    web_submission_link = reverse("web_questionnaire", args=[project_id])

    web_submission_link_disabled = 'disable_link'
    if 'web' in raw_project['value']['devices']:
        web_submission_link_disabled = ""

    create_subjects_link = ''
    if 'no' in raw_project['value']['activity_report']:
        create_subjects_link = append_query_strings_to_url(reverse("create_subject", args=[project.entity_type]),
                                                           web_view=True)

    project_info = dict(name=raw_project['value']['name'],
                        qid=questionnaire_code,
                        created=raw_project['value']['created'],
                        type=raw_project['value']['project_type'],
                        link=(reverse('project-overview', args=[project_id])),
                        log=log, analysis=analysis, disabled=disabled,
                        web_submission_link=web_submission_link,
                        web_submission_link_disabled=web_submission_link_disabled,
                        create_subjects_link=create_subjects_link,
                        entity_type=project.entity_type)
    return project_info


def get_project_list(request):
    projects = get_all_project_for_user(request.user)
    manager = get_database_manager(request.user)
    return [get_project_info(manager, project) for project in projects]


def projects_index(request):
    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)
    page_heading = get_page_heading(request.user)

    return disable_link_class, hide_link_class, page_heading


def get_subject_type_list(request):
    manager = get_database_manager(request.user)
    types = get_all_entity_types(manager)
    result = []
    for each in types:
        result.extend(each)
    return sorted(result)


@valid_web_user
def data_export(request):
    disable_link_class, hide_link_class, page_heading = projects_index(request)
    project_list = sorted(get_project_list(request), key=lambda x: x['name'])
    subject_types = sorted(get_subject_type_list(request))
    registered_subject_types = [each for each in subject_types if each != REPORTER_ENTITY_TYPE];
    return render_to_response('alldata/data_export.html',
                              {'subject_types': subject_types, 'registered_subject_types': registered_subject_types,
                               'projects': project_list, 'page_heading': page_heading,
                               'disable_link_class': disable_link_class,
                               'hide_link_class': hide_link_class, 'is_crs_admin': is_crs_admin(request),
                               'project_links': get_alldata_project_links(),
                               'is_quota_reached':is_quota_reached(request)},
                              context_instance=RequestContext(request))


def is_crs_admin(request):
    return get_organization(request).org_id == CRS_ORG_ID and not request.user.get_profile().reporter

def is_crs_user(request):
    return get_organization(request).org_id == CRS_ORG_ID


@login_required(login_url='/login')
@session_not_expired
@is_new_user
@is_not_expired
def index(request):
    disable_link_class, hide_link_class, page_heading = projects_index(request)
    project_list = get_project_list(request)

    smart_phone_instruction_link = reverse("smart_phone_instruction")

    activation_success = request.GET.get('activation', False)

    if is_crs_admin(request):
        return render_to_response('alldata/index.html',
                                  {'projects': project_list, 'page_heading': page_heading,
                                   'disable_link_class': disable_link_class,
                                   'hide_link_class': hide_link_class, 'is_crs_admin': True,
                                   'project_links': get_alldata_project_links(),
                                   'is_quota_reached':is_quota_reached(request),
                                   'activation_success': activation_success},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('alldata/index.html',
                                  {'projects': project_list, 'page_heading': page_heading,
                                   'disable_link_class': disable_link_class,
                                   'hide_link_class': hide_link_class, 'is_crs_admin': False,
                                   "smart_phone_instruction_link": smart_phone_instruction_link,
                                   'project_links': get_alldata_project_links(),
                                   'is_quota_reached':is_quota_reached(request),
                                   'activation_success': activation_success},
                                  context_instance=RequestContext(request))


@valid_web_user
def failed_submissions(request):
    disable_link_class, hide_link_class, page_heading = projects_index(request)
    logs = DatawinnerLog.objects.all()
    organization = get_organization(request)
    org_logs = [log for log in logs if log.organization == organization]
    return render_to_response('alldata/failed_submissions.html',
                              {'logs': org_logs, 'page_heading': page_heading,
                               'disable_link_class': disable_link_class,
                               'hide_link_class': hide_link_class, 'is_crs_admin': is_crs_admin(request),
                               'project_links': get_alldata_project_links(),
                               'is_quota_reached':is_quota_reached(request, organization=organization)},
                              context_instance=RequestContext(request))


@valid_web_user
@is_allowed_to_view_reports
def reports(request):
    report_list = get_reports_list(get_organization(request).org_id, request.session.get('django_language', 'en'))
    if not is_crs_user(request):
        raise Http404

    response = render_to_response('alldata/reports_page.html',
                                  {'reports': report_list, 'page_heading': "All Data",
                                   'project_links': get_alldata_project_links(),
                                   'is_quota_reached':is_quota_reached(request),
                                   'is_crs_admin': True},
                                  context_instance=RequestContext(request))
    response.set_cookie('crs_session_id', request.COOKIES['sessionid'])

    return response


@valid_web_user
def smart_phone_instruction(request):
    language_code = request.LANGUAGE_CODE
    instruction_template = "alldata/smart_phone_instruction_" + language_code + ".html"

    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)

    context = {'back_to_project_link': reverse("alldata_index"),
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
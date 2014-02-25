# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from mangrove.errors.MangroveException import DataObjectNotFound
from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired, valid_web_user
from datawinners.main.database import get_database_manager
from datawinners.project.submission.util import submission_stats
from mangrove.datastore.entity import get_by_short_code, Entity
from mangrove.datastore.queries import get_entities_by_type
from datawinners import settings
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.dashboard import helper

from datawinners.project.models import ProjectState, Project
from datawinners.project.wizard_view import edit_project
from mangrove.form_model.form_model import FormModel
from mangrove.transport import Channel
from datawinners.utils import get_map_key


def _find_reporter_name(dbm, row):
    try:
       if row.value["owner_uid"]:
           data_sender_entity = Entity.get(dbm, row.value["owner_uid"])
           name = data_sender_entity.value('name')
           return name
    except Exception:
        pass
    return ""


def _make_message(row):
    if row.value["status"]:
        message = " ".join(["%s: %s" % (k, v) for k, v in row.value["values"].items()])
    else:
        message = row.value["error_message"]
    return message

@login_required(login_url='/login')
@session_not_expired
@csrf_exempt
@is_not_expired
def get_submission_breakup(request, project_id):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, project_id)
    form_model = FormModel.get(dbm, project.qid)
    submission_success, submission_errors = submission_stats(dbm, form_model.form_code)
    response = json.dumps([submission_success, submission_errors])
    return HttpResponse(response)

@valid_web_user
def get_submissions_about_project(request, project_id):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, project_id)
    form_model = FormModel.get(dbm, project.qid)
    rows = dbm.load_all_rows_in_view('undeleted_survey_response', reduce=False, descending=True, startkey=[form_model.form_code, {}],
                                     endkey=[form_model.form_code], limit=7)
    submission_list = []
    for row in rows:
        reporter = _find_reporter_name(dbm, row)
        message = _make_message(row)
        submission = dict(message=message, created=row.value["submitted_on"].strftime("%B %d %y %H:%M"), reporter=reporter,
                          status=row.value["status"])
        submission_list.append(submission)

    submission_response = json.dumps(submission_list)
    return HttpResponse(submission_response)

def is_project_inactive(row):
    return row['value']['state'] == ProjectState.INACTIVE

@valid_web_user
@is_datasender
def dashboard(request):
    manager = get_database_manager(request.user)
    user_profile = NGOUserProfile.objects.get(user=request.user)
    organization = Organization.objects.get(org_id=user_profile.org_id)
    project_list = []
    rows = manager.load_all_rows_in_view('all_projects', descending=True, limit=8)
    for row in rows:
        link = reverse("project-overview", args=(row['value']['_id'],))
        project = dict(name=row['value']['name'], link=link, id=row['value']['_id'])
        project_list.append(project)
    language = request.session.get("django_language", "en")
    has_reached_sms_limit = organization.has_exceeded_message_limit()
    has_reached_submission_limit = organization.has_exceeded_submission_limit()
    message_box_deleted = []

    if "deleted" in request.GET.keys():
        message_box_deleted = [_('The questionnaire you are requesting for has been deleted from the system.')]
    return render_to_response('dashboard/home.html',
                              {"projects": project_list, 'trial_account': organization.in_trial_mode,
                               'has_reached_sms_limit':has_reached_sms_limit, 'message_box_deleted':message_box_deleted,
                               'has_reached_submission_limit':has_reached_submission_limit,
                               'language':language, 'counters':organization.get_counters()}, context_instance=RequestContext(request))


@valid_web_user
def start(request):
    text_dict = {'project': _('Projects'), 'datasenders': _('Data Senders'),
                 'subjects': _('Subjects'), 'alldata': _('Data Records')}

    tabs_dict = {'project': 'projects', 'datasenders': 'data_senders',
                 'subjects': 'subjects', 'alldata': 'all_data'}
    page = request.GET['page']
    page = page.split('/')
    url_tokens = [each for each in page if each != '']
    text = text_dict[url_tokens[-1]]
    return render_to_response('dashboard/start.html',
            {'text': text, 'title': text, 'active_tab': tabs_dict[url_tokens[-1]]},
                              context_instance=RequestContext(request))

@valid_web_user
def map_entities(request):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, request.GET['project_id'])
    if project.is_activity_report():
        entity_list = []
        for short_code in project.data_senders:
            try:
                entity = get_by_short_code(dbm, short_code, ["reporter"])
            except DataObjectNotFound:
                continue
            entity_list.append(entity)
    else:
        entity_list = get_entities_by_type(dbm, request.GET['id'])
    location_geojson = helper.create_location_geojson(entity_list)
    return HttpResponse(location_geojson)

def render_map(request):
    map_api_key = get_map_key(request.META['HTTP_HOST'])
    return render_to_response('maps/entity_map.html', {'map_api_key': map_api_key},context_instance=RequestContext(request))

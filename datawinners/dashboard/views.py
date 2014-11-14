# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json

from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _, ugettext, get_language
from django.views.decorators.csrf import csrf_exempt
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.datastore.entity import Entity, get_all_entities, by_short_codes

from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired, valid_web_user
from datawinners.main.database import get_database_manager
from datawinners.project.submission.util import submission_stats
from datawinners.accountmanagement.models import NGOUserProfile, Organization, PaymentDetails
from datawinners.utils import get_map_key
from mangrove.form_model.project import Project
from mangrove.utils.types import is_empty


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
        if message.find('| |') != -1:
            message = message.split('| |,')[['en', 'fr'].index(get_language())]
    return message


@login_required
@session_not_expired
@csrf_exempt
@is_not_expired
def get_submission_breakup(request, project_id):
    dbm = get_database_manager(request.user)
    questionnaire = Project.get(dbm, project_id)
    submission_success, submission_errors = submission_stats(dbm, questionnaire.id)
    response = json.dumps([submission_success, submission_errors])
    return HttpResponse(response)


@valid_web_user
def get_submissions_about_project(request, project_id):
    dbm = get_database_manager(request.user)
    questionnaire = Project.get(dbm, project_id)
    rows = dbm.load_all_rows_in_view('undeleted_survey_response', reduce=False, descending=True,
                                     startkey=[questionnaire.id, {}],
                                     endkey=[questionnaire.id], limit=7)
    submission_list = []
    for row in rows:
        reporter = _find_reporter_name(dbm, row)
        message = _make_message(row)
        submission = dict(message=message, created=row.value["submitted_on"].strftime("%B %d %y %H:%M"),
                          reporter=reporter,
                          status=row.value["status"])
        submission_list.append(submission)

    submission_response = json.dumps(submission_list)
    return HttpResponse(submission_response)


COST_MAP = {
        'Pro SMS': {'pay_monthly': 399,
                    'half_yearly': 2154,
                    'yearly': 3588
                    },
        'Pro': {'pay_monthly': 199,
                'half_yearly': 894,
                'yearly': 1188
               }
    }

def _fetch_amount(organization):
    payment_details = PaymentDetails.objects.filter(organization=organization)
    if is_empty(payment_details) or organization.account_type == 'Basic':
        return 0
    return COST_MAP[organization.account_type][payment_details[0].invoice_period]


@valid_web_user
@is_datasender
def dashboard(request):
    manager = get_database_manager(request.user)
    user_profile = NGOUserProfile.objects.get(user=request.user)
    organization = Organization.objects.get(org_id=user_profile.org_id)
    questionnaire_list = []
    rows = manager.load_all_rows_in_view('all_projects', descending=True, limit=8)
    for row in rows:
        link = reverse("project-overview", args=(row['value']['_id'],))
        questionnaire = dict(name=row['value']['name'], link=link, id=row['value']['_id'])
        questionnaire_list.append(questionnaire)
    language = request.session.get("django_language", "en")
    has_reached_sms_limit = organization.has_exceeded_message_limit()
    has_reached_submission_limit = organization.has_exceeded_submission_limit()
    questionnaire_does_not_exist = "NoExist" in request.GET.keys()

    if "deleted" in request.GET.keys():
        messages.info(request, ugettext('Sorry. The Questionnaire you are looking for has been deleted'),
                      extra_tags='error')

    context = {
        "projects": questionnaire_list, 'trial_account': organization.in_trial_mode,
        'has_reached_sms_limit': has_reached_sms_limit,
        'questionnaireDoesNotExist': questionnaire_does_not_exist,
        'has_reached_submission_limit': has_reached_submission_limit, 'language': language,
        'counters': organization.get_counters(),
        'first_time_activation': False,
        'account_cost': 0,
        'account_type': organization.account_type,
    }

    if request.session.get('activation_successful'):
        request.session.pop('activation_successful')
        context.update({
            'first_time_activation': True,
            'account_cost': _fetch_amount(organization)
        })

    return render_to_response('dashboard/home.html',
                              context, context_instance=RequestContext(request))


@valid_web_user
def start(request):
    text_dict = {'project': _('Questionnaires'), 'datasenders': _('Data Senders'),
                 'subjects': _('Identification Numbers'), 'alldata': _('Questionnaires')}

    title_dict = {'project': _('Questionnaires'), 'datasenders': _('Data Senders'),
                  'subjects': _('Identification Numbers'), 'alldata': _('Questionnaires')}

    tabs_dict = {'project': 'questionnaires', 'datasenders': 'data_senders',
                 'subjects': 'subjects', 'alldata': 'questionnaires'}
    page = request.GET['page']
    page = page.split('/')
    url_tokens = [each for each in page if each != '']
    text = text_dict[url_tokens[-1]]
    title = title_dict[url_tokens[-1]]
    return render_to_response('dashboard/start.html',
                              {'text': text, 'title': title, 'active_tab': tabs_dict[url_tokens[-1]]},
                              context_instance=RequestContext(request))


def _get_first_geocode_field_for_entity_type(dbm, entity_type):
    geocode_fields = [f for f in
                      dbm.view.registration_form_model_by_entity_type(key=[entity_type], include_docs=True)[0]["doc"][
                          "json_fields"] if
                      f["type"] == "geocode"]
    return geocode_fields[0] if len(geocode_fields) > 0 else None


def to_json_point(value):
    point_json = {"type": "Feature", "geometry":
        {
            "type": "Point",
            "coordinates": [
                value[1],
                value[0]
            ]
        }
    }
    return point_json


def get_location_list_for_entities(first_geocode_field, unique_ids):
    location_list = []
    for entity in unique_ids:
        value_dict = entity.data.get(first_geocode_field["name"])
        if value_dict and value_dict.has_key('value'):
            value = value_dict["value"]
            location_list.append(to_json_point(value))
    return location_list


@valid_web_user
def geo_json_for_project(request, project_id, entity_type=None):
    dbm = get_database_manager(request.user)
    location_list = []

    try:
        if entity_type:
            first_geocode_field = _get_first_geocode_field_for_entity_type(dbm, entity_type)
            if first_geocode_field:
                unique_ids = get_all_entities(dbm, [entity_type], limit=1000)
                location_list.extend(get_location_list_for_entities(first_geocode_field, unique_ids))
        else:
            questionnaire = Project.get(dbm, project_id)
            unique_ids = by_short_codes(dbm, questionnaire.data_senders, ["reporter"], limit=1000)
            location_list.extend(get_location_list_for_datasenders(unique_ids))

    except DataObjectNotFound:
        pass

    location_geojson = {"type": "FeatureCollection", "features": location_list}
    return HttpResponse(json.dumps(location_geojson))


def render_map(request):
    map_api_key = get_map_key(request.META['HTTP_HOST'])
    return render_to_response('maps/entity_map.html', {'map_api_key': map_api_key},
                              context_instance=RequestContext(request))


def get_location_list_for_datasenders(datasenders):
    location_list = []
    for entity in datasenders:
        geocode = entity.geometry
        if geocode:
            value = (geocode["coordinates"][0], geocode["coordinates"][1])
            location_list.append(to_json_point(value))
    return location_list

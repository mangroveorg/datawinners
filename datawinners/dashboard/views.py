# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _, ugettext, get_language
from django.views.decorators.csrf import csrf_exempt

from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired, valid_web_user
from datawinners.accountmanagement.models import NGOUserProfile, Organization, PaymentDetails
from datawinners.main.database import get_database_manager
from datawinners.preferences.models import UserPreferences
from datawinners.project.submission.util import submission_stats
from datawinners.utils import get_organization
from mangrove.datastore.entity import Contact
from mangrove.datastore.user_permission import get_questionnaires_for_user
from mangrove.form_model.project import Project
from mangrove.utils.types import is_empty


def _find_reporter_name(dbm, row):
    try:
        if row.value["owner_uid"]:
            data_sender_entity = Contact.get(dbm, row.value["owner_uid"])
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
    user_group = request.user.groups.all()[0].name

    organization = Organization.objects.get(org_id=user_profile.org_id)
    questionnaire_list = []
    if request.user.is_ngo_admin() or request.user.is_extended_user():
        rows = [row['value'] for row in manager.load_all_rows_in_view('all_projects', descending=True, limit=8)]
    else:
        rows = get_questionnaires_for_user(request.user.id, manager, descending=True, limit=8)
    for row in rows:
        if row.get('is_poll', False) is True:
            link = reverse("submissions", args=[row['_id'], row['form_code']])
        else:
            link = reverse("project-overview", args=(row['_id'],))
        questionnaire = dict(name=row['name'], link=link, id=row['_id'])
        questionnaire_list.append(questionnaire)
    language = request.session.get("django_language", "en")
    has_reached_sms_limit = organization.has_exceeded_message_limit()
    has_reached_submission_limit = organization.has_exceeded_submission_limit()
    questionnaire_does_not_exist = "NoExist" in request.GET.keys()

    if "deleted" in request.GET.keys():
        messages.info(request, ugettext('Sorry. The Questionnaire you are looking for has been deleted'),
                      extra_tags='error')
    user = request.user.id
    show_help = False if (UserPreferences.objects.filter(user=user)).count() > 0 else True


    context = {
        "show_help":show_help,
        "projects": questionnaire_list,
        'in_trial_mode': organization.in_trial_mode,
        'is_pro_sms': organization.is_pro_sms,
        'has_reached_sms_limit': has_reached_sms_limit,
        'questionnaireDoesNotExist': questionnaire_does_not_exist,
        'has_reached_submission_limit': has_reached_submission_limit, 'language': language,
        'counters': organization.get_counters(),
        'first_time_activation': False,
        'account_cost': 0,
        'account_type': organization.account_type,
        'user_group': user_group
    }

    if request.session.get('activation_successful'):
        request.session.pop('activation_successful')
        context.update({
            'first_time_activation': True,
            'account_cost': _fetch_amount(organization)
        })

    return render_to_response('dashboard/home.html',
                              context, context_instance=RequestContext(request))


def hide_help_element(request):
    user_id = request.user.id
    preference_name = "hide_help_element"
    preference_value = "True"
    help_element_preference = UserPreferences(user_id=user_id, preference_name=preference_name, preference_value=preference_value)
    help_element_preference.save()
    return HttpResponse(json.dumps({'success': True}))


@valid_web_user
def start(request):
    text_dict = {'project': _('Questionnaires'), 'datasenders': _('Data Senders'),
                 'subjects': _('Identification Numbers'), 'alldata': _('Questionnaires')}

    title_dict = {'project': _('Questionnaires'), 'datasenders': _('Data Senders'),
                  'subjects': _('Identification Numbers'), 'alldata': _('Questionnaires')}

    tabs_dict = {'project': 'questionnaires', 'datasenders': 'data_senders',
                 'subjects': 'subjects', 'alldata': 'questionnaires'}

    help_url_dict = {'project': 'https://www.datawinners.com/%s/find-answers-app/category/proj/?template=help',
                     'datasenders': 'https://www.datawinners.com/%s/find-answers-app/category/allds/?template=help',
                     'subjects': 'https://www.datawinners.com/%s/find-answers-app/category/idnos/?template=help',
                     'alldata': 'https://www.datawinners.com/%s/find-answers-app/category/proj/?template=help'}

    page = request.GET['page']
    page = page.split('/')
    url_tokens = [each for each in page if each != '']
    text = text_dict[url_tokens[-1]]
    title = title_dict[url_tokens[-1]]
    help_url = help_url_dict[url_tokens[-1]] % _("wp_language")
    return render_to_response('dashboard/start.html',
                              {'text': text, 'title': title, 'active_tab': tabs_dict[url_tokens[-1]],
                               'help_url': help_url, 'is_pro_sms': get_organization(request).is_pro_sms},
                              context_instance=RequestContext(request))


def _get_all_reporter_fields():
    all_fields = {}
    all_fields['short_code'] = _("Unique ID")
    all_fields['name'] = _("Name")
    all_fields['telephone_number'] = _("Mobile Number")
    all_fields['email'] = _("Email Address")
    all_fields['location'] = _("Location")
    all_fields['geo_code'] = _("GPS Coordinates")
    all_fields['devices'] = _("Devices")
    all_fields['is_data_sender'] = ""
    return all_fields

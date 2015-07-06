import ast
from datetime import datetime
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import DEACTIVATE_POLL, ACTIVATE_POLL
from datawinners.sent_message.models import PollInfo
from django.utils.translation import ugettext as _
from datawinners.utils import get_organization
from mangrove.datastore.entity import contact_by_short_code
from mangrove.form_model.project import Project, get_active_form_model_name_and_id
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from datawinners.accountmanagement.decorators import is_not_expired, is_datasender, session_not_expired
from datawinners.common.lang.utils import get_available_project_languages
from datawinners.main.database import get_database_manager
from datawinners.project.helper import is_project_exist
from datawinners.project.views.views import get_project_link


def _is_same_questionnaire(question_id_active, questionnaire):
    if questionnaire.id == question_id_active:
        is_active = True
    else:
        is_active = False
    return is_active


def _get_number_of_recipients_(project_id):
    num_of_recipients = 0
    poll_submissions = PollInfo.objects.filter(questionnaire_id=project_id)
    for poll_submission in poll_submissions:
        num_of_recipients += len(ast.literal_eval(poll_submission.recipients))
    return num_of_recipients


def _construct_poll_recipients(poll_submission):
    poll_recipient_map = {}
    poll_recipients = ast.literal_eval(poll_submission.recipients)
    for poll_recipient in poll_recipients:
        poll_recipient_name, poll_recipient_id = poll_recipient.split("(")
        poll_recipient_map.update({poll_recipient_name: poll_recipient_id.strip(")")})
    return poll_recipient_map


def _get_poll_sent_messages_info(project_id):
    messages_poll_info_array = []
    poll_submissions = PollInfo.objects.filter(questionnaire_id=project_id)
    for poll_submission in poll_submissions:
        messages = {}
        messages['sent_on'] = poll_submission.sent_on[:-3]
        messages['message'] = poll_submission.message
        poll_recipient_map = _construct_poll_recipients(poll_submission)
        messages['poll_recipient_map'] = poll_recipient_map
        poll_sender = poll_submission.sender.split('(')

        poll_sender_map = {poll_sender[0]: poll_sender[1].strip(")")}

        messages['sender'] = poll_sender_map
        messages_poll_info_array.append(messages)
    return messages_poll_info_array


@login_required
@csrf_exempt
@is_not_expired
@is_project_exist
def get_poll_sent_messages(request, project_id):
    messages_poll_info_array = _get_poll_sent_messages_info(project_id)
    return HttpResponse(json.dumps({'success': True, 'poll_messages': messages_poll_info_array}))



@login_required
@csrf_exempt
@is_not_expired
@is_project_exist
@is_datasender
def get_poll_info(request, project_id):
    manager = get_database_manager(request.user)
    questionnaire = Project.get(manager, project_id)
    project_links = get_project_link(questionnaire)
    questionnaire_active, active_poll_id, active_poll_name = get_active_form_model_name_and_id(manager)
    from_date = questionnaire.modified.date()
    to_date = questionnaire.end_date.date()
    languages_list = get_available_project_languages(manager)
    current_project_language = questionnaire.language
    num_of_recipients = _get_number_of_recipients_(project_id)
    return render_to_response('project/poll.html', RequestContext(request, {
        'project': questionnaire,
        'message_text': questionnaire.form_fields[0]['label'],
        'project_links': project_links,
        'is_active': questionnaire.active,
        'from_date': from_date,
        'is_pro_sms': get_organization(request).is_pro_sms,
        'to_date': to_date,
        'questionnaire_id': active_poll_id,
        'questionnaire_name': active_poll_name,
        'languages_list': json.dumps(languages_list),
        'languages_link': reverse('languages'),
        'current_project_language': current_project_language,
        'post_url': reverse("project-language", args=[questionnaire.id]),
        'get_poll_sent_messages': reverse("get_poll_sent_messages", args=[questionnaire.id]),
        'questionnaire_code': questionnaire.form_code,
        'num_of_recipients': num_of_recipients,
    }))

def _change_questionnaire_status(questionnaire, active_status):
    questionnaire.active = active_status
    questionnaire.save()


def _change_questionnaire_end_date(questionnaire, end_date):
    questionnaire.end_date = end_date
    questionnaire.save()


@login_required
@csrf_exempt
@is_not_expired
@is_project_exist
def deactivate_poll(request, project_id):
    if request.method == 'POST':
        manager = get_database_manager(request.user)
        questionnaire = Project.get(manager, project_id)
        if questionnaire:
            _change_questionnaire_status(questionnaire, "deactivated")
            UserActivityLog().log(request, action=DEACTIVATE_POLL, project=questionnaire.name,
                                  detail=questionnaire.name)
            return HttpResponse(json.dumps({'success': True}))
        return HttpResponse(json.dumps({'success': False}))


def _create_reponse_for_activated_poll(manager, questionnaire, request):
    is_active, question_id_active, question_name_active = get_active_form_model_name_and_id(manager)
    is_current_active = _is_same_questionnaire(question_id_active, questionnaire)
    end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%dT%H:%M:%S')
    if is_current_active:
        _change_questionnaire_end_date(questionnaire, end_date)
        return {'success': True}
    elif not is_active and not is_current_active:
        _change_questionnaire_status(questionnaire, "active")
        _change_questionnaire_end_date(questionnaire, end_date)
        UserActivityLog().log(request, action=ACTIVATE_POLL, project=questionnaire.name,
                              detail=questionnaire.name)
        return {'success': True}
    message = _(
        "To activate the Poll you must first deactivate your current Poll %s. You may only have one active Poll at a time.") % question_name_active
    return {'success': False, 'message': message,
                    'question_id_active': question_id_active,
                    'question_name_active': question_name_active}


@login_required
@csrf_exempt
@is_not_expired
@is_project_exist
def activate_poll(request, project_id):
    if request.method == 'POST':
        manager = get_database_manager(request.user)
        questionnaire = Project.get(manager, project_id)
        if questionnaire:
            response_dict =_create_reponse_for_activated_poll(manager, questionnaire, request)
            return HttpResponse(json.dumps(response_dict))
        return HttpResponse(json.dumps({'success': False, 'message': "No Such questionnaire"}))


def _get_poll_recipients(dbm, questionnaire):
    datasender_ids = questionnaire.data_senders
    contact_dict = {}
    for datasender_id in datasender_ids:
        contact = contact_by_short_code(dbm, datasender_id)
        if contact.name != '':
            contact_dict[contact.name] = contact.short_code
        else:
            contact_dict[contact.data.get('mobile_number')['value']] = contact.short_code
    return contact_dict


@login_required
@session_not_expired
@is_datasender
@is_not_expired
@is_project_exist
def my_poll_recipients_count(request, project_id):
    dbm = get_database_manager(request.user)
    questionnaire = Project.get(dbm, project_id)
    contact_dict = _get_poll_recipients(dbm, questionnaire)
    return HttpResponse(content_type='application/json', content=json.dumps({'my_poll_recipients': contact_dict}))
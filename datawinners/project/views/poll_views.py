from datetime import datetime
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from mangrove.form_model.project import Project, is_active_form_model
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from datawinners.accountmanagement.decorators import is_not_expired, is_datasender
from datawinners.common.lang.utils import get_available_project_languages
from datawinners.main.database import get_database_manager
from datawinners.project.helper import is_project_exist
from datawinners.project.views.views import get_project_link


def _is_active(questionnaire):
    is_active = False
    if questionnaire.active == "active":
        is_active = True
    return is_active


def _is_same_questionnaire(question_id_active, questionnaire):
    if questionnaire.id == question_id_active:
        is_active = True
    else:
        is_active = False
    return is_active


@login_required
@csrf_exempt
@is_not_expired
@is_project_exist
@is_datasender
def poll(request, project_id):
    manager = get_database_manager(request.user)
    questionnaire = Project.get(manager, project_id)
    project_links = get_project_link(questionnaire)
    is_active = _is_active(questionnaire)
    questionnaire_active, question_id_active, question_name_active = is_active_form_model(manager)
    from_date = questionnaire.modified.date()
    to_date = questionnaire.end_date.date()
    languages_list = get_available_project_languages(manager)
    current_project_language = questionnaire.language

    return render_to_response('project/poll.html', RequestContext(request, {
        'project': questionnaire,
        'project_links': project_links,
        'is_active': is_active,
        'from_date': from_date,
        'to_date': to_date,
        'questionnaire_id': question_id_active,
        'questionnaire_name': question_name_active,
        'languages_list': json.dumps(languages_list),
        'languages_link': reverse('languages'),
        'current_project_language': current_project_language,
        'post_url': reverse("project-language", args=[questionnaire.id]),
        'questionnaire_code': questionnaire.form_code
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
def deactivate_poll(request, project_id):
    if request.method == 'POST':
        manager = get_database_manager(request.user)
        questionnaire = Project.get(manager, project_id)
        if questionnaire:
            _change_questionnaire_status(questionnaire, "deactivated")
            return HttpResponse(json.dumps({'success': True}))
        return HttpResponse(json.dumps({'success': False}))


@login_required
@csrf_exempt
@is_not_expired
def activate_poll(request, project_id):
    if request.method == 'POST':
        manager = get_database_manager(request.user)
        questionnaire = Project.get(manager, project_id)
        if questionnaire:
            is_active, question_id_active, question_name_active = is_active_form_model(manager)
            is_current_active = _is_same_questionnaire(question_id_active, questionnaire)
            end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%dT%H:%M:%S')
            if not is_active and not is_current_active:
                _change_questionnaire_status(questionnaire, "active")
                _change_questionnaire_end_date(questionnaire, end_date)
                return HttpResponse(json.dumps({'success': True}))
            elif is_current_active:
                _change_questionnaire_end_date(questionnaire, end_date)
                return HttpResponse(json.dumps({'success': True}))
        return HttpResponse(json.dumps({'success': False, 'message': "No Such questionnaire"}))

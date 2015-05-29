import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from datawinners.accountmanagement.decorators import is_not_expired, is_datasender
from datawinners.main.database import get_database_manager
from datawinners.project.helper import is_project_exist
from datawinners.project.utils import make_project_links
from datawinners.project.views.views import get_project_link
from mangrove.form_model.project import Project, is_active_form_model
from django.template.context import RequestContext
from django.core.urlresolvers import reverse


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
    is_active = _is_same_questionnaire(question_id_active, questionnaire)
    from_date = questionnaire.modified.date()
    to_date = questionnaire.end_date.date()

    return render_to_response('project/poll.html', RequestContext(request, {
        'project': questionnaire,
        'project_links': project_links,
        'is_active': is_active,
        'from_date': from_date,
        'to_date': to_date,
        'questionnaire_id': question_id_active,
        'questionnaire_name': question_name_active
    }))


def _change_questionnaire_status(questionnaire, active_status):
    questionnaire.active = active_status
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
            return HttpResponse(
                    json.dumps({'success': True}))
        return HttpResponse(
                    json.dumps({'success': False}))

@login_required
@csrf_exempt
@is_not_expired
def activate_poll(request, project_id):
    if request.method == 'POST':
        manager = get_database_manager(request.user)
        questionnaire = Project.get(manager, project_id)
        if questionnaire:
            is_active, question_id_active, question_name_active = is_active_form_model(manager)
            is_active = _is_same_questionnaire(question_id_active, questionnaire)
            if not is_active:
                _change_questionnaire_status(questionnaire, "active")
                return HttpResponse(
                    json.dumps({'success': True}))
            return HttpResponse(
                    json.dumps({'success': False, 'message': "Another poll is already active."}))
        return HttpResponse(
                    json.dumps({'success': False, 'message': "No Such questionnaire"}))

import json
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.main.utils import get_database_manager
from datawinners.project import helper
from datawinners.project.forms import CreateProject
from datawinners.project.models import Project, ProjectState
from datawinners.project.views import project_overview
from mangrove.datastore.documents import attributes
from mangrove.datastore.entity_type import get_all_entity_types
from mangrove.errors.MangroveException import DataObjectAlreadyExists, QuestionCodeAlreadyExistsException, EntityQuestionAlreadyExistsException, FormModelDoesNotExistsException
from django.contrib import messages
from mangrove.form_model.form_model import REPORTER, FormModel, get_form_model_by_code
from mangrove.utils.types import is_string

def create_questionnaire(post, manager, entity_type, name):
    entity_type = [entity_type] if is_string(entity_type) else entity_type
    questionnaire_code = post['questionnaire-code']
    json_string = post['question-set']
    question_set = json.loads(json_string)
    form_model = FormModel(manager, entity_type=entity_type, name=name, type='survey', state=attributes.TEST_STATE, fields=[], form_code=questionnaire_code)
    return helper.update_questionnaire_with_questions(form_model, question_set, manager)


def _get_element_from(data, index):
    return data.split('=')[index]


def _get_form_data(post):
    data_list = post.split('&')
    return {_get_element_from(i,0): _get_element_from(i,1) for i in data_list}


@login_required()
def save_project(request):
    manager = get_database_manager(request.user)
    entity_list = get_all_entity_types(manager)
    entity_list = helper.remove_reporter(entity_list)
    form = CreateProject(data=_get_form_data(request.POST['profile_form']), entity_list=entity_list)
    try:
        get_form_model_by_code(manager, request.POST['questionnaire-code'])
        return HttpResponseServerError('ERROR!!!')
    except FormModelDoesNotExistsException:
        if form.is_valid():
            entity_type = form.cleaned_data['entity_type']
            project = Project(name=form.cleaned_data["name"], goals=form.cleaned_data["goals"],
                              project_type='survey', entity_type=entity_type,
                              reminder_and_deadline=helper.new_deadline_and_reminder(form.cleaned_data),
                              activity_report=form.cleaned_data['activity_report'],
                              state = ProjectState.TEST)
            try:
                form_model = create_questionnaire(post=request.POST, manager=manager, entity_type=entity_type, name=form.cleaned_data["name"])
            except QuestionCodeAlreadyExistsException as e:
                return HttpResponseServerError(e)
            except EntityQuestionAlreadyExistsException as e:
                return HttpResponseServerError(e.message)

            try:
                pid = project.save(manager)
                qid = form_model.save()
                project.qid = qid
                pid = project.save(manager)
            except DataObjectAlreadyExists as e:
                messages.error(request, e.message)
                return render_to_response('project/create_project.html', {'form': form},
                                          context_instance=RequestContext(request))
            return HttpResponse(json.dumps({"response": "ok", 'redirect_url': reverse(project_overview, args=[pid])}))

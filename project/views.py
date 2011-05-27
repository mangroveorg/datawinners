# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from copy import copy

import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.main.utils import get_database_manager
from datawinners.project.forms import ProjectProfile
from datawinners.project.models import Project
import helper
from datawinners.project import models
from mangrove.datastore.entity import get_all_entity_types
from mangrove.errors.MangroveException import QuestionCodeAlreadyExistsException, EntityQuestionAlreadyExistsException, DataObjectAlreadyExists
from mangrove.form_model.field import field_to_json
from mangrove.form_model.form_model import get_form_model_by_code, FormModel
from mangrove.transport.submissions import get_submissions_made_for_questionnaire
from django.contrib import messages

PAGE_SIZE = 4


@login_required(login_url='/login')
def questionnaire(request):
    manager = get_database_manager(request)
    if request.method == 'GET':
        pid = request.GET["pid"]
        project = models.get_project(pid, manager)
        form_model = helper.load_questionnaire(manager, project.qid)
        existing_questions = json.dumps(form_model.fields, default=field_to_json)
        return render_to_response('project/questionnaire.html',
                                  {"existing_questions": existing_questions, "questionnaire_code": form_model.form_code,
                                   'project_id': pid}, context_instance=RequestContext(request))


@login_required(login_url='/login')
def create_profile(request):
    manager = get_database_manager(request)
    entity_list = get_all_entity_types(manager)
    if request.method == 'GET':
        form = ProjectProfile(entity_list=entity_list)
        return render_to_response('project/profile.html', {'form': form}, context_instance=RequestContext(request))

    form = ProjectProfile(data=request.POST, entity_list=entity_list)
    if form.is_valid():
        project = Project(name=form.cleaned_data["name"], goals=form.cleaned_data["goals"],
                          project_type=form.cleaned_data['project_type'], entity_type=form.cleaned_data['entity_type'],
                          devices=form.cleaned_data['devices'])
        form_model = helper.create_questionnaire(post=form.cleaned_data, dbm=manager)
        try:
            pid = project.save(manager)
            qid = form_model.save()
            project.qid = qid
            pid = project.save(manager)
        except DataObjectAlreadyExists as e:
            messages.error(request,e.message)
            return render_to_response('project/profile.html', {'form': form}, context_instance=RequestContext(request))
        return HttpResponseRedirect('/project/questionnaire?pid=' + pid)
    else:
        return render_to_response('project/profile.html', {'form': form}, context_instance=RequestContext(request))


def edit_profile(request):
    manager = get_database_manager(request)
    entity_list = get_all_entity_types(manager)
    if request.method == 'GET':
        project = models.get_project(request.GET['pid'], dbm=manager)
        form = ProjectProfile(data=project, entity_list=entity_list)
        return render_to_response('project/profile.html', {'form': form}, context_instance=RequestContext(request))

    project = models.get_project(request.GET['pid'], dbm=manager)
    form = ProjectProfile(data=request.POST, entity_list=entity_list)
    if form.is_valid():
        project.update(manager, form.cleaned_data)
        project.update_questionnaire(manager)

        try:
            pid = project.save(manager)
        except DataObjectAlreadyExists as e:
            messages.error(request,e.message)
            return render_to_response('project/profile.html', {'form': form}, context_instance=RequestContext(request))
        return HttpResponseRedirect('/project/questionnaire?pid=' + pid)
    else:
        return render_to_response('project/profile.html', {'form': form}, context_instance=RequestContext(request))


def save_questionnaire(request):
    manager = get_database_manager(request)
    if request.method == 'POST':
        questionnaire_code = request.POST['questionnaire-code']
        question_set = json.loads(request.POST['question-set'])

        pid = request.POST['pid']
        project = models.get_project(pid, dbm=manager)
        form_model = manager.get(project.qid, FormModel)
        try:
            form_model = helper.update_questionnaire_with_questions(form_model, question_set, manager)
        except QuestionCodeAlreadyExistsException as e:
            return HttpResponseServerError(e.message)
        except EntityQuestionAlreadyExistsException as e:
            return HttpResponseServerError(e.message)
        else:
            try:
                form_model.form_code = questionnaire_code
            except DataObjectAlreadyExists as e:
                return HttpResponseServerError(e.message)
            form_model.name = project.name
            form_model.entity_id = project.entity_type
            form_model.save()
            return HttpResponse("Your questionnaire has been saved")


@login_required(login_url='/login')
def project_listing(request):
    project_list = []
    rows = models.get_all_projects(dbm=get_database_manager(request))
    for row in rows:
        link = "/project/overview?pid=" + row['value']['_id']
        project = dict(name=row['value']['name'], created=row['value']['created'], type=row['value']['project_type'],
                       link=link)
        project_list.append(project)
    return render_to_response('project/all.html', {'projects': project_list}, context_instance=RequestContext(request))


@login_required(login_url='/login')
def project_overview(request):
    manager = get_database_manager(request)
    project = models.get_project(request.GET["pid"], dbm=manager)
    link = '/project/profile/edit?pid=' + request.GET["pid"]
    questionnaire = helper.load_questionnaire(manager, project['qid'])
    number_of_questions = len(questionnaire.fields)
    result_link = '/project/results/%s' % questionnaire.form_code
    project_overview = dict(what=number_of_questions, how=project['devices'], link=link, result_link=result_link)
    return render_to_response('project/overview.html', {'project': project_overview},
                              context_instance=RequestContext(request))


def get_number_of_rows_in_result(dbm, questionnaire_code):
    submissions_count = get_submissions_made_for_questionnaire(dbm, questionnaire_code, count_only=True)
    if submissions_count:
        return submissions_count[0]
    return None


def get_submissions_for_display(current_page, dbm, questionnaire_code, questions):
    submissions = get_submissions_made_for_questionnaire(dbm, questionnaire_code, page_number=current_page,
                                                         page_size=PAGE_SIZE, count_only=False)
    submissions = helper.get_submissions(questions, submissions)
    return submissions


@login_required(login_url='/login')
def project_results(request, questionnaire_code=None):
    current_page = int(request.GET.get('page_number') or 1)
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if request.GET.get('filters'):
        filters = json.loads(request.GET.get('filters'))
    contains = request.GET.get('contains')
    manager = get_database_manager(request)
    form_model = get_form_model_by_code(manager, questionnaire_code)
    questionnaire = (questionnaire_code, form_model.name)
    questions = helper.get_code_and_title(form_model.fields)
    rows = get_number_of_rows_in_result(manager, questionnaire_code)
    if rows:
        submissions = get_submissions_for_display(current_page - 1, manager, questionnaire_code, copy(questions))
        results = {
            'questionnaire': questionnaire,
            'questions': questions,
            'submissions': submissions
        }

        return render_to_response('project/results.html',
                                  {'questionnaire_code': questionnaire_code, 'results': results, 'pages': rows,
                                   current_page: current_page},
                                  context_instance=RequestContext(request)
                                  )
    return HttpResponse("No submissions present for this project")

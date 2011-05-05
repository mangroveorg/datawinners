# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import datetime
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.project.forms import ProjectProfile
from datawinners.project.models import Project
import helper
from mangrove.datastore.database import get_db_manager
from datawinners.project import models
from mangrove.errors.MangroveException import QuestionCodeAlreadyExistsException, EntityQuestionAlreadyExistsException
from mangrove.form_model.field import field_to_json
from mangrove.form_model.form_model import get

@login_required(login_url='/login')
def questionnaire(request):
    if request.method == 'GET':
        pid = request.GET["pid"]
        project=models.get_project(pid)
        form_model = helper.load_questionnaire(project.qid)
        existing_questions = json.dumps(form_model.fields, default=field_to_json)
        return render_to_response('project/questionnaire.html', {"existing_questions": existing_questions,"questionnaire_code":form_model.form_code,'project_id':pid},context_instance=RequestContext(request))


@login_required(login_url='/login')
def create_profile(request):
    if request.method == 'GET':
        form = ProjectProfile()
        return render_to_response('project/profile.html', {'form': form}, context_instance=RequestContext(request))

    form = ProjectProfile(request.POST)
    if form.is_valid():
        project = Project(name=form.cleaned_data["name"], goals=form.cleaned_data["goals"],
                          project_type=form.cleaned_data['project_type'], entity_type=form.cleaned_data['entity_type'],
                          devices=form.cleaned_data['devices'])
        form_model = helper.create_questionnaire(post=form.cleaned_data)
        qid = form_model.save()
        project.qid=qid
        pid=project.save()
        return HttpResponseRedirect('/project/questionnaire?pid='+pid)
    else:
        return render_to_response('project/profile.html', {'form': form}, context_instance=RequestContext(request))

def edit_profile(request):

    if request.method == 'GET':
        project=models.get_project(request.GET['pid'])
        form = ProjectProfile(project)
        return render_to_response('project/profile.html',{'form':form},context_instance=RequestContext(request))

    project=models.get_project(request.GET['pid'])
    form = ProjectProfile(request.POST)
    if form.is_valid():
        project.update(form.cleaned_data)
        pid = project.save()
        return HttpResponseRedirect('/project/questionnaire?pid='+ pid)
    else:
        return render_to_response('project/profile.html', {'form': form}, context_instance=RequestContext(request))

def save_questionnaire(request):
    if request.method == 'POST':
        questionnaire_code = request.POST['questionnaire-code']
        question_set = json.loads(request.POST['question-set'])

        pid = request.POST['pid']
        project=models.get_project(pid)
        form_model = get(get_db_manager(), project.qid)
        try:
            form_model = helper.update_questionnaire_with_questions(form_model, question_set)
        except QuestionCodeAlreadyExistsException as e:
            return HttpResponseServerError(e.message)
        except EntityQuestionAlreadyExistsException as e:
            return HttpResponseServerError(e.message)
        else:
            form_model.form_code = questionnaire_code
            form_model.name = project.name
            form_model.entity_id = project.entity_type
            form_model.save()
            return HttpResponse("Your questionnaire has been saved")

@login_required(login_url='/login')
def project_listing(request):
    project_list=[]
    rows = models.get_all_projects()
    for row in rows:
       link = "/project/overview?pid="+row['value']['_id']
       project= dict(name=row['value']['name'],created=row['value']['created'],type=row['value']['project_type'],link=link)
       project_list.append(project)
    return render_to_response('project/all.html',{'projects':project_list}, context_instance=RequestContext(request))

@login_required(login_url='/login')
def project_overview(request):
    project=models.get_project(request.GET["pid"])
    link = '/project/profile/edit?pid='+request.GET["pid"]
    number_of_questions =len(helper.load_questionnaire(project['qid']).fields)
    project_overview=dict(what=number_of_questions,how=project['devices'],link=link)
    return render_to_response('project/overview.html',{'project':project_overview},context_instance=RequestContext(request))

@login_required(login_url='/login')
def project_results(request, questionnaire_code = None):
#    Load the data records corresponding to the questionnaire here
    results = {
                'questions' : [('Q1Code', 'Q1Text', 'Q1Description',), ('Q2Code', 'Q2Text', 'Q2Description',)],
                'submissions' : [(datetime.utcnow(), 'Q1 Ans', 'Q2 Ans',), (datetime.utcnow(), None, 'Q2 Ans',)]
              }
    return render_to_response('project/results.html',{'questionnaire_code': questionnaire_code, 'results': results})

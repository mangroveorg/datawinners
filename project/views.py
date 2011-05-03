# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.decorators import method_decorator
from datawinners.project.forms import ProjectProfile
from datawinners.project.models import Project
import helper
from mangrove.datastore.database import get_db_manager
from mangrove.form_model.form_model import get, FormModel
from datawinners.project import models

@login_required(login_url='/login')
def questionnaire(request):
    qid = request.GET["qid"]
    form_model = helper.load_questionnaire(qid)
    existing_questions = json.dumps(form_model.fields)
    request.session["qid"] = qid
    return render_to_response('project/questionnaire.html', {"existing_questions": existing_questions},
                              context_instance=RequestContext(request))

@login_required(login_url='/login')
def complete_profile(request):
    if request.method == 'GET':
        form = ProjectProfile()
        return render_to_response('project/profile.html', {'form': form}, context_instance=RequestContext(request))
    form = ProjectProfile(request.POST)
    if form.is_valid():
        project = Project(name=form.cleaned_data["name"], goals=form.cleaned_data["goals"],
                          project_type=form.cleaned_data['project_type'], entity_type=form.cleaned_data['entity_type'],
                          devices=form.cleaned_data['device'])
        form_model = helper.create_questionnaire(post=form.cleaned_data)
        qid = form_model.save()
        project.qid=qid
        project.save()
        return HttpResponseRedirect('/project/questionnaire?qid='+qid)

def save_questionnaire(request):
    if request.method == 'POST':
        questionnaire_code = request.POST['questionnaire-code']
        post_dictionary = json.loads(request.POST['question-set'])
        form_model = get(get_db_manager(), request.session["qid"])
        form_model = helper.save_questionnaire(form_model, post_dictionary)
        form_model.form_code = questionnaire_code
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
    project_overview=dict(what=3,how=project['devices'])
    return render_to_response('project/overview.html',{'project':project_overview})
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.project.forms import ProjectSetUp
import helper
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.form_model import get

@login_required(login_url='/login')
def questionnaire(request):
    qid = request.GET["qid"]
    form_model=helper.load_questionnaire(qid)
    existing_questions=json.dumps(form_model.fields)
    print existing_questions
    request.session["qid"] = qid
    return render_to_response('project/questionnaire.html', {"existing_questions":existing_questions}, context_instance=RequestContext(request))

@login_required(login_url='/login')
def set_up_questionnaire(request):
    if request.method == 'GET':
        form=ProjectSetUp()
        return render_to_response('project/setup_questionnaire.html',{'form':form},context_instance=RequestContext(request))
    form = ProjectSetUp(request.POST)
    if form.is_valid():
        form_model=helper.create_questionnaire(form.cleaned_data)
        qid=form_model.save()
        return HttpResponseRedirect('/project/questionnaire?qid='+qid)

def save_questionnaire(request):
    if request.method == 'POST':
        post_dictionary =json.loads(request.POST.keys()[0])
        print post_dictionary
        form_model=get(get_db_manager(),request.session["qid"])
        form_model=helper.save_questionnaire(form_model,post_dictionary)
        form_model.save()
    return HttpResponse("Your questionnaire has been saved")
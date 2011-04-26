# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.project.forms import ProjectSetUp
import helper
from mangrove.datastore.database import get_db_manager

@login_required(login_url='/login')

def questionnaire(request):
    return render_to_response('project/questionnaire.html', context_instance=RequestContext(request))

def set_up_questionnaire(request):
    form=ProjectSetUp()
    return render_to_response('project/setup_questionnaire.html',{'form':form},context_instance=RequestContext(request))

def save_questionnaire(request):
    if request.method == 'POST':
        post_dictionary =json.loads(request.POST.keys()[0])
        form_model=helper.create_questionnaire(post_dictionary, get_db_manager())
        form_model.save()
    return HttpResponse("Your questionnaire has been saved")
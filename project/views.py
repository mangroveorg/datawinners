# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import helper
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.form_model import FormModel

@login_required(login_url='/login')

def questionnaire(request):

    return render_to_response('project/questionnaire.html', context_instance=RequestContext(request))

def save_questionnaire(request):
    if request.method == 'POST':
        post_dictionary =json.loads(request.POST.keys()[0])
        form_model=helper.create_questionnaire(post_dictionary, get_db_manager())
        form_model.save()

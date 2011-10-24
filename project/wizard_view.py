from django.shortcuts import render_to_response
from datawinners.project.forms import CreateProject

from django.template.context import RequestContext

def questionnaire_wizard(request):
    if request.method == 'GET':
        form = CreateProject()
    return render_to_response('project/create_project.html', {'form':form},context_instance=RequestContext(request))

def new_project_overview(request):
    return render_to_response('project/new_overview.html')
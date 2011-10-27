from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.project.forms import CreateProject

@login_required(login_url='/login')
def new_create_project(request):
    if request.method == 'GET':
        form = CreateProject()
        return render_to_response('project/create_project.html', {'form':form},context_instance=RequestContext(request))
    form = CreateProject(data=request.POST, entity_list=entity_list)
    if form.is_valid():
        return HttpResponseRedirect(reverse(new_project_overview))
    else:
        return render_to_response('project/create_project.html', {'form':form},context_instance=RequestContext(request))

def new_project_overview(request):
    return render_to_response('project/overview.html')


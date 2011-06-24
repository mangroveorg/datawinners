# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import json
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from datawinners.main.utils import get_database_manager
from mangrove.datastore import data
from mangrove.form_model.form_model import FormModel
from mangrove.transport.reporter import find_reporter

def get_submissions(dbm, form_code):
    rows = dbm.load_all_rows_in_view('submissionlog', reduce=False, descending=True, startkey=[form_code, {}],
                                         endkey=[form_code], limit=7)

    submission_list =  []
    for row in rows:
        reporter = find_reporter(dbm, row.value["source"])
        reporter = reporter[0]["name"]
        submission = dict(error_message=row.value["error_message"], created=row.value["submitted_on"], reporter=reporter)
        submission_list.append(submission)
    return submission_list

@login_required(login_url='/login')
def dashboard(request):
    manager = get_database_manager(request)

    project_list = []
    rows = manager.load_all_rows_in_view('all_projects', descending=True, limit=4)
    for row in rows:
        link = reverse("project-overview",args=(row['value']['_id'],))

        form_model = manager.get(row['value']['qid'], FormModel)
        questionnaire_code = form_model.form_code
        submissions = get_submissions(manager, questionnaire_code)

        project = dict(name=row['value']['name'], link=link, submissions=submissions)
        project_list.append(project)

    return render_to_response('dashboard/home.html',
                              {"projects": project_list}, context_instance=RequestContext(request))

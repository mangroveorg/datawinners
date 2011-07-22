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
from mangrove.form_model.field import field_to_json
from mangrove.transport.reporter import find_reporter

def get_submissions(dbm, form_code):
    rows = dbm.load_all_rows_in_view('submissionlog', reduce=False, descending=True, startkey=[form_code, {}],
                                         endkey=[form_code], limit=7)

    submission_list = []
    submission_success = 0
    submission_errors = 0
    if rows is not None:
        for row in rows:
            phone_number = row.value["source"]
            if phone_number <> 'xls':
                reporter = find_reporter(dbm, row.value["source"])
                reporter = reporter[0]["name"]
                if row.value["status"]:
                    message = " ".join(["%s: %s" % (k, v) for k, v in row.value["values"].items()])
                else:
                    message = row.value["error_message"]
                submission = dict(message=message, created=row.value["submitted_on"], reporter=reporter,
                                  status=row.value["status"])
                submission_list.append(submission)

        rows = dbm.load_all_rows_in_view('submissionlog', startkey=[form_code], endkey=[form_code, {}],
                                         group=True, group_level=1, reduce=True)
        for row in rows:
            submission_success = row["value"]["success"]
            submission_errors = row["value"]["count"] - row["value"]["success"]

    return submission_list, submission_success, submission_errors

@login_required(login_url='/login')
def dashboard(request):
    manager = get_database_manager(request)

    project_list = []
    rows = manager.load_all_rows_in_view('all_projects', descending=True, limit=4)
    for row in rows:
        link = reverse("project-overview",args=(row['value']['_id'],))

        form_model = manager.get(row['value']['qid'], FormModel)
        questionnaire_code = form_model.form_code
        submissions, success, errors = get_submissions(manager, questionnaire_code)

        project = dict(name=row['value']['name'], link=link, submissions=submissions, success=success, errors=errors)
        project_list.append(project)

    return render_to_response('dashboard/home.html',
                              {"projects": project_list}, context_instance=RequestContext(request))

@login_required(login_url='/login')
def start(request):
    text_dict = {'project': 'Projects', 'datasenders': 'Data Senders',
                 'subjects': 'Subjects', 'alldata': 'Data Records'}

    tabs_dict = {'project': 'projects', 'datasenders': 'data_senders',
                 'subjects': 'subjects', 'alldata': 'all_data'}
    page = request.GET['page']
    page = page.split('/')
    url_tokens = [each for each in page if each !='']
    text = text_dict[url_tokens[-1]]
    return render_to_response('dashboard/start.html', {'text': text, 'title': text, 'active_tab': tabs_dict[url_tokens[-1]]},
                              context_instance=RequestContext(request))

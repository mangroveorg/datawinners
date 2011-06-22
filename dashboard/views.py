# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.main.utils import get_database_manager
from datawinners.project import helper
from datawinners.project.views import get_number_of_rows_in_result
from mangrove.transport.submissions import get_submissions_made_for_questionnaire
from mangrove.datastore import data

@login_required(login_url='/login')
def dashboard(request):
    manager = get_database_manager(request)

    #Deadlines and reminders

    #Projects
    project_list = []
    rows = get_projects(dbm=manager)
    for row in rows:
        #Submissions
        submissions = []
        questionnaire = helper.load_questionnaire(manager, row['value']['qid'])
        questionnaire_code = questionnaire.form_code
        submission_counts = get_number_of_rows_in_result(manager, questionnaire_code)
        if submission_counts:
            submissions = get_submissions_made_for_questionnaire(manager, questionnaire_code, page_number=0,
                                                         page_size=6, count_only=False)


        link = "/project/overview?pid=" + row['value']['_id']
        project = dict(name=row['value']['name'], link=link, submissions=submissions)
        project_list.append(project)

    return render_to_response('dashboard/home.html',
                              {"projects": project_list}, context_instance=RequestContext(request))

def get_projects(dbm):
    rows = dbm.load_all_rows_in_view('all_projects', skip=0, limit=4)

    return rows

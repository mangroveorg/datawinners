from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from mangrove.form_model.form_model import  FormModel
from datawinners.accountmanagement.httpauth import logged_in_or_basicauth
from datawinners.alldata.helper import get_all_project_for_user
from datawinners.main.utils import get_database_manager


@logged_in_or_basicauth()
def formList(request):
    rows = get_all_project_for_user(request.user)
    projects = [(row['value']['name'], row['value']['qid']) for row in rows]

    base_url = request.build_absolute_uri().replace(request.path, "")
    return render_to_response(
        "xforms/odk_list_forms.xml",
            {"projects": projects,
             "base_url": base_url},
        mimetype="text/xml",
        context_instance=RequestContext(request))


@csrf_exempt
def submission(request):
    context = RequestContext(request)
    show_options = True
    # request.FILES is a django.utils.datastructures.MultiValueDict
    # for each key we have a list of values
    if show_options:
        context.domain = Site.objects.get(id=1).domain
        response = render_to_response("xforms/submission.html",
            context_instance=context)
    else:
        response = HttpResponse()
    response.status_code = 201
    response['Location'] = "http://10.12.6.209:8443/xforms/submission"
    return response


@logged_in_or_basicauth()
def xform(request, questionnaire_code=None):
    questionnaire = FormModel.get(get_database_manager(request.user), questionnaire_code)

    return render_to_response(
        "xforms/xform.xml",
            {"questionnaire": questionnaire},
        mimetype="text/xml",
        context_instance=RequestContext(request))

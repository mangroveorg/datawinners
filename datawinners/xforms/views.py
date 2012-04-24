from django.shortcuts import render_to_response
from django.template.context import RequestContext
from mangrove.form_model.form_model import get_form_model_by_code, FormModel
from datawinners.accountmanagement.httpauth import logged_in_or_basicauth
from datawinners.alldata.helper import get_all_project_for_user
from datawinners.main.utils import get_database_manager


@logged_in_or_basicauth()
def formList(request):
    rows = get_all_project_for_user(request.user)
    projects = [(row['value']['name'], row['value']['qid']) for row in rows]

    return render_to_response(
        "xforms/odk_list_forms.xml",
            {"projects": projects},
        mimetype="text/xml",
        context_instance=RequestContext(request))

@logged_in_or_basicauth()
def xform(request, questionnaire_code=None):

    questionnaire = FormModel.get(get_database_manager(request.user), questionnaire_code)

    return render_to_response(
        "xforms/xform.xml",
            {"questionnaire": questionnaire},
        mimetype="text/xml",
        context_instance=RequestContext(request))

import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datawinners.accountmanagement.decorators import valid_web_user, is_datasender
from datawinners.main.database import get_database_manager
from datawinners.preferences.models import ProjectPreferences
from mangrove.form_model.form_model import get_form_model_by_code


@valid_web_user
@is_datasender
@csrf_exempt
def hide_submission_log_column(request):
    user = request.user
    post_data = json.loads(request.POST.get('data'))
    preference_name = post_data.get('tab') + "_hide_column"
    visible = post_data.get('visible')
    preference_value = post_data.get('column')
    form_code = post_data.get('questionnaire_code')
    manager = get_database_manager(request.user)
    questionnaire = get_form_model_by_code(manager, form_code)
    if not visible:
        preference = ProjectPreferences(user_id=user.id, project_id=questionnaire.id,
                                                     preference_name=preference_name, preference_value=preference_value)
        preference.save()
    else:
        preferences = ProjectPreferences.objects.filter(user=user, project_id=questionnaire.id,
                                                        preference_name=preference_name,
                                                        preference_value=preference_value)

        for preference in preferences:
            preference.delete()
    return HttpResponse(json.dumps({'success': True}))


# @valid_web_user
# @is_datasender
# @csrf_exempt
def get_hidden_columns(request):
    user = request.user
    post_data = json.loads(request.POST.get('data'))
    preference_name = post_data.get('tab') + "_hide_column"
    form_code = post_data.get('questionnaire_code')
    manager = get_database_manager(request.user)
    questionnaire = get_form_model_by_code(manager, form_code)
    preferences = ProjectPreferences.objects.filter(user=user, project_id=questionnaire.id,
                                                    preference_name=preference_name)
    hide_columns = []
    for preference in preferences:
            hide_columns.append(int(preference.preference_value))
    return HttpResponse(mimetype='application/json', content=json.dumps({"hide_columns": hide_columns}))

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
    user_id = request.user.id
    preference_name = "submission_log_hide_column"
    post_data = json.loads(request.POST.get('data'))
    preference_value = post_data.get('hide_column')
    form_code = post_data.get('questionnaire_code')
    manager = get_database_manager(request.user)
    questionnaire = get_form_model_by_code(manager, form_code)
    help_element_preference = ProjectPreferences(user_id=user_id, project_id=questionnaire.id,
                                                 preference_name=preference_name, preference_value=preference_value)
    help_element_preference.save()
    return HttpResponse(json.dumps({'success': True}))

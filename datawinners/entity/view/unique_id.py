import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from datawinners.accountmanagement.decorators import is_datasender
from datawinners.common.constant import DELETED_IDENTIFICATION_NUMBER
from datawinners.entity.helper import delete_entity_instance
from datawinners.entity.views import log_activity, get_success_message
from datawinners.main.database import get_database_manager
from datawinners.search.entity_search import SubjectQuery
from mangrove.form_model.form_model import get_form_model_by_entity_type, header_fields
from mangrove.transport import TransportInfo


@csrf_view_exempt
@csrf_response_exempt
@login_required
@is_datasender
def delete_subjects(request):
    manager = get_database_manager(request.user)
    entity_type = request.POST['entity_type']
    all_ids = _subject_short_codes_to_delete(request, manager, entity_type)

    transport_info = TransportInfo("web", request.user.username, "")
    delete_entity_instance(manager, all_ids, entity_type, transport_info)
    log_activity(request, DELETED_IDENTIFICATION_NUMBER, "%s: [%s]" % (entity_type.capitalize(), ", ".join(all_ids)))
    message = get_success_message(entity_type)
    return HttpResponse(json.dumps({'success': True, 'message': message}))


def _subject_short_codes_to_delete(request, manager, entity_type):
    if request.POST.get("all_selected") == 'true':
        search_query = request.POST.get('search_query')
        subject_list = SubjectQuery().query(request.user, entity_type, search_query)
        form_model = get_form_model_by_entity_type(manager, [entity_type])
        short_code_index = header_fields(form_model).keys().index("short_code")
        return [s[short_code_index] for s in subject_list]

    return request.POST['all_ids'].split(';')
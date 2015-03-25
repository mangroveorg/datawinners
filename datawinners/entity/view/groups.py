import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datawinners.accountmanagement.decorators import session_not_expired, is_datasender, is_not_expired
from datawinners.entity.group_helper import get_group_details
from datawinners.main.database import get_database_manager
from mangrove.datastore.entity import contact_by_short_code


@login_required
@session_not_expired
@is_datasender
@is_not_expired
def get_group_names(request):
    dbm = get_database_manager(request.user)
    group_names = get_group_details(dbm)
    return HttpResponse(json.dumps({'group_names': group_names}), content_type="application/json")

@login_required
@session_not_expired
@is_datasender
@is_not_expired
def assign_contact_to_groups(request):
    dbm = get_database_manager(request.user)
    group_names = json.loads(request.POST['group-names'])
    current_group_name = request.POST['current_group_name']
    contact_ids = json.loads(request.POST['contact_ids'])
    for contact_id in contact_ids:
        contact = contact_by_short_code(dbm, contact_id)
        for group_name in group_names:
            contact.add_custom_group(group_name)
        contact.save()

    return HttpResponse(content= json.dumps({'success': True}), content_type='application/json')


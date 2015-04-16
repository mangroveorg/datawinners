import json
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.utils.http import int_to_base36
from datawinners.accountmanagement.decorators import is_super_admin

@is_super_admin
def generate_token_for_datasender_activate(request):
    user = User.objects.get(username=request.POST['ds_email'])
    token = default_token_generator.make_token(user)
    return HttpResponse(json.dumps({'token': token, 'user_id': int_to_base36(user.id)}),
                        content_type='application/json')


def check_if_datasender_entry_made_in_postgres(request):
    try:
        user_count = User.objects.filter(email__in=[request.POST['ds_email']]).count()
        found = True if user_count > 0 else False
    except Exception:
        found = False
    return HttpResponse(json.dumps({'found': found}), content_type='application/json')

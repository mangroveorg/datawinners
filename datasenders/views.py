# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from _csv import Error
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_response_exempt, csrf_view_exempt
from django.http import HttpResponse
from datawinners import import_data as import_module
import json


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
def index(request):
    all_data_senders = import_module.load_all_reporters(request)
    if request.method == 'POST':
        error_message, failure_imports, success, success_message = import_module.import_data(request, True)
        return HttpResponse(json.dumps({'success': success, 'message': success_message, 'error_message': error_message,
                                    'failure_imports': failure_imports, 'all_data':all_data_senders}))

    return render_to_response('datasender/index.html', {'all_data': all_data_senders}, context_instance=RequestContext(request))


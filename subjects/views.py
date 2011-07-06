# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.decorators.http import require_http_methods
from datawinners.subjects.SubjectException import InvalidFileFormatException
from mangrove.errors.MangroveException import CSVParserInvalidHeaderFormatException, XlsParserInvalidHeaderFormatException
from datawinners import import_data as import_module




@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
def index(request):
    if request.method == 'POST':
        error_message, failure_imports, success, success_message = import_module.import_data(request)
        all_subjects = import_module.load_all_subjects(request)
        return HttpResponse(json.dumps({'success': success, 'message': success_message, 'error_message': error_message,
                                    'failure_imports': failure_imports, 'all_data':all_subjects}))

    all_subjects = import_module.load_all_subjects(request)
    return render_to_response('subjects/index.html', {'all_data': all_subjects}, context_instance=RequestContext(request))



@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
@login_required(login_url='/login')
def import_subjects_from_project_wizard(request):
    error_message, failure_imports, success, success_message = import_module.import_data(request)
    return HttpResponse(json.dumps({'success': success, 'message': success_message, 'error_message': error_message,
                                    'failure_imports': failure_imports}))

# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.auth.decorators import login_required

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.main.utils import get_database_manager
from datawinners.subjects.forms import SubjectUploadForm
from django.contrib import messages
from mangrove.datastore.entity import get_all_entities
from mangrove.errors.MangroveException import CSVParserInvalidHeaderFormatException
from mangrove.transport.player.player import CsvPlayer, CsvParser
from mangrove.transport.submissions import SubmissionHandler


def handle_uploaded_file(request):
    file = request.FILES['file']
    manager = get_database_manager(request)
    csv_player = CsvPlayer(dbm=manager, submission_handler=SubmissionHandler(manager), parser=CsvParser())
    response = csv_player.accept(file)
    return response


def laod_all_subjects(request):
    rows = get_all_entities(dbm=get_database_manager(request), include_docs=True)
    data = []
    for row in rows:
        id = row['id']
        name = row['doc']['short_code']
        short_code = row['doc']['short_code']
        type = row['doc']['aggregation_paths']['_type']
        type = '.'.join(type)
        location = row['doc']['geometry'].get('coordinates')
        result_dict = dict(id=id, name=name, short_name=short_code, type=type, location=location)
        data.append(result_dict)
    return data


def tabulate_output(rows):
    tabulated_data = []
    for row in rows:
        tabulated_data.append(row.errors)
    return tabulated_data

@login_required(login_url='/login')
def index(request):
    failure_imports = None
    if request.method == 'POST':
        form = SubjectUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                response = handle_uploaded_file(request)
                success = len([index for index in response if index.success])
                total = len(response)
                failure = [index for index in response if not index.success]
                failure_imports = tabulate_output(failure)
                messages.info(request, '%s of %s records uploaded' % (success, total))
            except CSVParserInvalidHeaderFormatException as e:
                messages.error(request, e.message)
    else:
        form = SubjectUploadForm()
    all_subjects = laod_all_subjects(request)
    return render_to_response('subjects/index.html', {'form': form, 'all_subjects': all_subjects,'failure_data':failure_imports},
                              context_instance=RequestContext(request))
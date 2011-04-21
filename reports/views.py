# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.auth.decorators import login_required
from django.forms.widgets import Select

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from mangrove.datastore import data
from mangrove.datastore.entity import load_all_entity_types
from reports.forms import Report, ReportHierarchy
from mangrove.datastore.database import get_db_manager

@login_required(login_url='/login')
def report(request):
    manager = get_db_manager()
    column_headers = []
    values = []
    if request.method == 'POST':
        form = Report(request.POST)
        if form.is_valid():
            entity_type = form.cleaned_data['entity_type'].split(".")
            filter_criteria = form.cleaned_data['filter']
            filter = {'location': filter_criteria.split(",")} if filter_criteria else None
            report_data = data.fetch(manager, entity_type=entity_type,
                                     aggregates={"director":data.reduce_functions.LATEST,
                                                 "beds": "latest",
                                                 "patients": "sum"},
                                     filter=filter
            )
            column_headers,values = tabulate_output(report_data,"Clinic_id")
    else:
        form = Report()
    return render_to_response('reports/reportperlocation.html', {'form': form,'column_headers':column_headers,'column_values':values},
                              context_instance=RequestContext(request))

def tabulate_output(report_data,first_column_name):
    for id, record in report_data.items():
        record[first_column_name] = id
    id, info = report_data.items()[0] if report_data.items() else ("", {})
    column_headers = info.keys()
    column_headers.sort()
    information = [v for k, v in report_data.items()]
    values = []
    for row in information:
        values.append([row[h] for h in column_headers])
    return column_headers,values

@login_required(login_url='/login')
def hierarchy_report(request):
    manager = get_db_manager()
    column_headers,values = [],[]
    if request.method == 'POST':
        form = ReportHierarchy(request.POST)
        if form.is_valid():
            aggregates_field = form.cleaned_data['aggregates_field']
            reduce_function=form.cleaned_data['reduce']
            aggregates={aggregates_field:reduce_function}
            aggregate_on_path = form.cleaned_data['aggregate_on_path']
            level=form.cleaned_data['level']
            aggregate_on={'type': aggregate_on_path,"level":level}
            report_data = data.fetch(manager, entity_type=["Health_Facility", "Clinic"],
                             aggregates=aggregates,
                             aggregate_on=aggregate_on,
                             )
            column_headers,values = tabulate_output(report_data,"Path")
    else:
        form = ReportHierarchy()

    return render_to_response('reports/reportperhierarchypath.html', {'form': form,'column_headers':column_headers,'column_values':values},
                          context_instance=RequestContext(request))


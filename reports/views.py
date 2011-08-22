# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.main.utils import get_database_manager
from mangrove.datastore import data
from datawinners.reports.forms import Report, ReportHierarchy
from mangrove.datastore.data import TypeAggregration, LocationFilter
from mangrove.datastore.entity import get_all_entity_types


@login_required(login_url='/login')
def report(request):
    manager = get_database_manager(request.user)
    types = get_all_entity_types(manager)
    choices = [('.'.join(t), '.'.join(t)) for t in types]
    column_headers = []
    values = []
    error_message = None
    if request.method == 'POST':
        form = Report(data=request.POST, choices=choices)
        if form.is_valid():
            entity_type = form.cleaned_data['entity_type'].split(".")
            filter_criteria = form.cleaned_data['filter']
            aggregates_field = form.cleaned_data['aggregates_field']
            location = filter_criteria.split(",") if filter_criteria else None
            report_data = data.aggregate(manager, entity_type=entity_type,
                                         aggregates={aggregates_field: data.reduce_functions.LATEST},
                                         filter=LocationFilter(location=location)
            )
            column_headers, values = tabulate_output(report_data, "ID")
            if not len(values):
                error_message = 'Sorry, No records found for this query'
    else:
        form = Report(choices=choices)
    return render_to_response('reports/reportperlocation.html', {'form': form, 'column_headers': column_headers,
                                                                 'column_values': values,
                                                                 'error_message': error_message},
                              context_instance=RequestContext(request))


def tabulate_output(report_data, first_column_name):
    for id, record in report_data.items():
        record[first_column_name] = id
    id, info = report_data.items()[0] if report_data.items() else ("", {})
    column_headers = info.keys()
    column_headers.sort()
    information = [v for k, v in report_data.items()]
    values = []
    for row in information:
        values.append([row[h] for h in column_headers])
    return column_headers, values


@login_required(login_url='/login')
def hierarchy_report(request):
    manager = get_database_manager(request.user)
    column_headers, values = [], []
    choices = [(t, '.'.join(t)) for t in get_all_entity_types(manager)]

    if request.method == 'POST':
        form = ReportHierarchy(data=request.POST, choices=choices)
        if form.is_valid():
            entity_type = form.cleaned_data['entity_type'].split(".")
            aggregates_field = form.cleaned_data['aggregates_field']
            reduce_function = form.cleaned_data['reduce']
            aggregates = {aggregates_field: reduce_function}
            aggregate_on_path = form.cleaned_data['aggregate_on_path']
            level = form.cleaned_data['level']
            report_data = data.aggregate(manager, entity_type=entity_type,
                                         aggregates=aggregates,
                                         aggregate_on=TypeAggregration(type=aggregate_on_path, level=level),
                                         )
            column_headers, values = tabulate_output(report_data, "Path")
    else:
        form = ReportHierarchy(choices=choices)

    return render_to_response('reports/reportperhierarchypath.html',
            {'form': form, 'column_headers': column_headers, 'column_values': values},
                              context_instance=RequestContext(request))

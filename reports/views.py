import datetime
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from mangrove.datastore.database import get_db_manager
from mangrove.datastore import data
from reports.forms import Report

def report(request):
    if request.method == 'POST':
        form = Report(request.POST)
        if form.is_valid():
            entity_type = form.cleaned_data['entity_type'].split(",")
            filter_criteria = form.cleaned_data['filter']
            filter = { 'location' : filter_criteria.split(",")} if filter_criteria else None
            report_data = data.fetch(get_db_manager(),entity_type=entity_type,
                                aggregates = {  "director" : "latest" ,
                                                 "beds" : "latest" ,
                                                 "patients" : "sum"  },
                                filter = filter
                                )
            print report_data
            for id, record in report_data.items():
                record["Clinic_id"] = id
            id, info= report_data.items()[0] if report_data.items() else ("",{})
            form.column_headers = info.keys()
            form.column_headers.sort()
            information = [v for k, v in report_data.items()]
            form.values = []
            for row in information:
                form.values.append([row[h] for h in form.column_headers])
    else:
        form = Report()
    return render_to_response('reports/reportperlocation.html', {'form' : form},context_instance=RequestContext(request))


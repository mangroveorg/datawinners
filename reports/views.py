from django.shortcuts import render_to_response
from django.template.context import RequestContext
from mangrove.datastore.database import get_db_manager
from mangrove.datastore import data
from reports.forms import Report

def report(request):
    form = Report()
    form.entity_type = "Clinic"
    report_data = data.fetch(get_db_manager(),entity_type=["Health_Facility","Clinic"],
                            aggregates = {  "director" : "latest" ,
                                             "beds" : "latest" ,
                                             "patients" : "sum"  },
                            aggregate_on = { 'type' : 'entity'},
                            filter = { 'location' : ['India','MH','Pune']}
                            )
    for id, record in report_data.items():
        record["Clinic_id"] = id
    id, info= report_data.items()[0]
    form.column_headers = info.keys()
    form.column_headers.sort()
    information = [v for k, v in report_data.items()]
    form.values = []
    for row in information:
        form.values.append([row[h] for h in form.column_headers])
    return render_to_response('reports/reportperlocation.html', {'form' : form},context_instance=RequestContext(request))

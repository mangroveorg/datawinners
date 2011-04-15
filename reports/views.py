import datetime
from pytz import UTC
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from mangrove.datastore.database import get_db_manager, _delete_db_and_remove_db_manager
from mangrove.datastore import data
from reports.forms import Report
from datawinners.reports.forms import HierarchyReport
from mangrove.datastore.entity import Entity
from mangrove.datastore.database import get_db_manager


def report(request):
    form = Report()
    form.entity_type = "Clinic"
    report_data = data.fetch(get_db_manager(), entity_type=["Health_Facility", "Clinic"],
                             aggregates={"director": "latest",
                                         "beds": "latest",
                                         "patients": "sum"},
                             aggregate_on={'type': 'entity'},
                             filter={'location': ['India', 'MH', 'Pune']}
    )
    for id, record in report_data.items():
        record["Clinic_id"] = id
    id, info = report_data.items()[0]
    form.column_headers = info.keys()
    form.column_headers.sort()
    information = [v for k, v in report_data.items()]
    form.values = []
    for row in information:
        form.values.append([row[h] for h in form.column_headers])
    return render_to_response('reports/reportperlocation.html', {'form': form},
                              context_instance=RequestContext(request))


def hierarchy_report(request):
    form = HierarchyReport()
    form.entity_type = "Clinic"
    manager = get_db_manager('http://localhost:5984/', 'mangrove-hierarchy')
    LoadData(manager).load_data_for_hierarchy_report()

    result_set = data.fetch(manager,entity_type=["Health_Facility", "Clinic"],
                           aggregates = {  "patients" : "sum"  },
                           aggregate_on = { 'type' : 'location', "level" : 2},
                           )
    form.values = {"a":1}
    col=[]
    rows=[]
    values =[]
    for k in result_set.items()[0][1]:
        col.append(k)
    form.column_headers = col
    for k in result_set:
        rows.append(k)
        values.append(result_set[k])
    form.rows = rows
    form.values = values
    

    _delete_db_and_remove_db_manager(manager)
    return render_to_response('reports/reportperhierarchypath.html', {'form': form},
                              context_instance=RequestContext(request))


class LoadData:
    def __init__(self,manager):
        self.manager = manager
    def load_data_for_hierarchy_report(self):

        ENTITY_TYPE = ["Health_Facility", "Clinic"]
        FEB = datetime.datetime(2011, 02, 01, tzinfo=UTC)
        MARCH = datetime.datetime(2011, 03, 01, tzinfo=UTC)

        # Entities for State 1: Maharashtra
        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Pune'])
        id1 = e.save()

        e.add_data(data=[("beds", 300), ("meds", 20), ("director", "Dr. A"), ("patients", 10)],
                   event_time=FEB)
        e.add_data(data=[("beds", 500), ("meds", 20), ("patients", 20)],
                   event_time=MARCH)

        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Pune'])
        id2 = e.save()
        e.add_data(data=[("beds", 100), ("meds", 10), ("director", "Dr. AA"), ("patients", 50)],
                   event_time=FEB)
        e.add_data(data=[("beds", 200), ("meds", 20), ("patients", 20)],
                   event_time=MARCH)

        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Mumbai'])
        id3 = e.save()
        e.add_data(data=[("beds", 100), ("meds", 10), ("director", "Dr. AAA"), ("patients", 50)],
                   event_time=FEB)
        e.add_data(data=[("beds", 200), ("meds", 20), ("patients", 50)],
                   event_time=MARCH)

        # Entities for State 2: karnataka
        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'Karnataka', 'Bangalore'])
        id4 = e.save()
        e.add_data(data=[("beds", 100), ("meds", 250), ("director", "Dr. B1"), ("patients", 50)],
                   event_time=FEB)
        e.add_data(data=[("beds", 200), ("meds", 400), ("director", "Dr. B2"), ("patients", 20)],
                   event_time=MARCH)
        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'Karnataka', 'Hubli'])
        id5 = e.save()
        e.add_data(data=[("beds", 100), ("meds", 250), ("director", "Dr. B1"), ("patients", 50)],
                   event_time=FEB)
        e.add_data(data=[("beds", 200), ("meds", 400), ("director", "Dr. B2"), ("patients", 20)],
                   event_time=MARCH)


        # Entities for State 3: Kerala
        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'Kerala', 'Kochi'])
        id6 = e.save()
        e.add_data(data=[("beds", 200), ("meds", 50), ("director", "Dr. C"), ("patients", 12)],
                   event_time=MARCH)

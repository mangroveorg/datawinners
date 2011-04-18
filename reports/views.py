# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import datetime
from pytz import UTC
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from mangrove.datastore.database import get_db_manager, _delete_db_and_remove_db_manager
from mangrove.datastore import data
from reports.forms import Report, ReportHierarchy
from mangrove.datastore.entity import Entity
from mangrove.datastore.database import get_db_manager


def report(request):
    manager = get_db_manager()
    data_set=DataFormatter()
    if request.method == 'POST':
        form = Report(request.POST)
        if form.is_valid():
            entity_type = form.cleaned_data['entity_type'].split(",")
            filter_criteria = form.cleaned_data['filter']
            filter = {'location': filter_criteria.split(",")} if filter_criteria else None
            report_data = data.fetch(manager, entity_type=entity_type,
                                     aggregates={"director":data.reduce_functions.LATEST,
                                                 "beds": "latest",
                                                 "patients": "sum"},
                                     filter=filter
            )
            data_set.tabulate_output(report_data,"Clinic_id")
    else:
        form = Report()
    return render_to_response('reports/reportperlocation.html', {'form': form,'dataset':data_set},
                              context_instance=RequestContext(request))

class DataFormatter(object):

    def tabulate_output(self, report_data,first_column_name):
        for id, record in report_data.items():
            record[first_column_name] = id
        id, info = report_data.items()[0] if report_data.items() else ("", {})
        self.column_headers = info.keys()
        self.column_headers.sort()
        information = [v for k, v in report_data.items()]
        self.values = []
        for row in information:
            self.values.append([row[h] for h in self.column_headers])


def hierarchy_report(request):
    manager = get_db_manager()
#    LoadData(manager).load_data_for_hierarchy_report()
    data_set=DataFormatter()
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
            print report_data
            data_set.tabulate_output(report_data,"Path")
    else:
        form = ReportHierarchy()

#    report_data = data.fetch(manager, entity_type=["Health_Facility", "Clinic"],
#                             aggregates={"patients": "sum"},
#                             aggregate_on={'type': 'location', "level": 2},
#                             )

#    _delete_db_and_remove_db_manager(manager)
    return render_to_response('reports/reportperhierarchypath.html', {'form': form,'data_set':data_set},
                          context_instance=RequestContext(request))

class LoadData:
    def __init__(self, manager):
        self.manager = manager

    def load_data_for_hierarchy_report(self):
        ENTITY_TYPE = ["Health_Facility", "Clinic"]
        FEB = datetime.datetime(2011, 02, 01, tzinfo=UTC)
        MARCH = datetime.datetime(2011, 03, 01, tzinfo=UTC)

        # Entities for State 1: Maharashtra
        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Pune'])
        e.set_aggregation_path("governance",["Director","Med_Officer","Surgeon"])
        id1 = e.save()

        e.add_data(data=[("beds", 300), ("meds", 20), ("director", "Dr. A"), ("patients", 10)],
                   event_time=FEB)
        e.add_data(data=[("beds", 500), ("meds", 20), ("patients", 20)],
                   event_time=MARCH)

        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Pune'])
        e.set_aggregation_path("governance",["Director","Med_Supervisor","Surgeon"])
        id2 = e.save()
        e.add_data(data=[("beds", 100), ("meds", 10), ("director", "Dr. AA"), ("patients", 50)],
                   event_time=FEB)
        e.add_data(data=[("beds", 200), ("meds", 20), ("patients", 20)],
                   event_time=MARCH)

        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Mumbai'])
        e.set_aggregation_path("governance",["Director","Med_Officer","Doctor"])
        id3 = e.save()
        e.add_data(data=[("beds", 100), ("meds", 10), ("director", "Dr. AAA"), ("patients", 50)],
                   event_time=FEB)
        e.add_data(data=[("beds", 200), ("meds", 20), ("patients", 50)],
                   event_time=MARCH)

        # Entities for State 2: karnataka
        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'Karnataka', 'Bangalore'])
        e.set_aggregation_path("governance",["Director","Med_Supervisor","Nurse"])
        id4 = e.save()
        e.add_data(data=[("beds", 100), ("meds", 250), ("director", "Dr. B1"), ("patients", 50)],
                   event_time=FEB)
        e.add_data(data=[("beds", 200), ("meds", 400), ("director", "Dr. B2"), ("patients", 20)],
                   event_time=MARCH)
        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'Karnataka', 'Hubli'])
        e.set_aggregation_path("governance",["Director","Med_Officer","Surgeon"])
        id5 = e.save()
        e.add_data(data=[("beds", 100), ("meds", 250), ("director", "Dr. B1"), ("patients", 50)],
                   event_time=FEB)
        e.add_data(data=[("beds", 200), ("meds", 400), ("director", "Dr. B2"), ("patients", 20)],
                   event_time=MARCH)


        # Entities for State 3: Kerala
        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'Kerala', 'Kochi'])
        e.set_aggregation_path("governance",["Director","Med_Officer","Nurse"])
        id6 = e.save()
        e.add_data(data=[("beds", 200), ("meds", 50), ("director", "Dr. C"), ("patients", 12)],
                   event_time=MARCH)

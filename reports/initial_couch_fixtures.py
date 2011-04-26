# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
from mangrove.datastore.entity import Entity, define_type
from mangrove.datastore.database import get_db_manager
from pytz import UTC
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined

def load_data():
    manager = get_db_manager()
    ENTITY_TYPE = ["Health_Facility", "Clinic"]
    FEB = datetime.datetime(2011, 02, 01, tzinfo=UTC)
    MARCH = datetime.datetime(2011, 03, 01, tzinfo=UTC)


    #  Default Entity Types
    try:
        define_type(manager, "Reporter")
    except EntityTypeAlreadyDefined:
        pass

    # Entities for State 1: Maharashtra
    e = Entity(manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Pune'])
    e.set_aggregation_path("governance",["Director","Med_Officer","Surgeon"])
    e.save()

    e.add_data(data=[("beds", 300), ("meds", 20), ("director", "Dr. A"), ("patients", 10)],
               event_time=FEB)
    e.add_data(data=[("beds", 500), ("meds", 20), ("patients", 20)],
               event_time=MARCH)

    e = Entity(manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Pune'])
    e.set_aggregation_path("governance",["Director","Med_Supervisor","Surgeon"])
    e.save()
    e.add_data(data=[("beds", 100), ("meds", 10), ("director", "Dr. AA"), ("patients", 50)],
               event_time=FEB)
    e.add_data(data=[("beds", 200), ("meds", 20), ("patients", 20)],
               event_time=MARCH)

    e = Entity(manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Mumbai'])
    e.set_aggregation_path("governance",["Director","Med_Officer","Doctor"])
    e.save()
    e.add_data(data=[("beds", 100), ("meds", 10), ("director", "Dr. AAA"), ("patients", 50)],
               event_time=FEB)
    e.add_data(data=[("beds", 200), ("meds", 20), ("patients", 50)],
               event_time=MARCH)

    # Entities for State 2: karnataka
    e = Entity(manager, entity_type=ENTITY_TYPE, location=['India', 'Karnataka', 'Bangalore'])
    e.set_aggregation_path("governance",["Director","Med_Supervisor","Nurse"])
    e.save()
    e.add_data(data=[("beds", 100), ("meds", 250), ("director", "Dr. B1"), ("patients", 50)],
               event_time=FEB)
    e.add_data(data=[("beds", 200), ("meds", 400), ("director", "Dr. B2"), ("patients", 20)],
               event_time=MARCH)
    e = Entity(manager, entity_type=ENTITY_TYPE, location=['India', 'Karnataka', 'Hubli'])
    e.set_aggregation_path("governance",["Director","Med_Officer","Surgeon"])
    e.save()
    e.add_data(data=[("beds", 100), ("meds", 250), ("director", "Dr. B1"), ("patients", 50)],
               event_time=FEB)
    e.add_data(data=[("beds", 200), ("meds", 400), ("director", "Dr. B2"), ("patients", 20)],
               event_time=MARCH)


    # Entities for State 3: Kerala
    e = Entity(manager, entity_type=ENTITY_TYPE, location=['India', 'Kerala', 'Kochi'])
    e.set_aggregation_path("governance",["Director","Med_Officer","Nurse"])
    e.save()
    e.add_data(data=[("beds", 200), ("meds", 50), ("director", "Dr. C"), ("patients", 12)],
               event_time=MARCH)



  
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
from mangrove.datastore.entity import Entity, define_type
from mangrove.datastore.database import get_db_manager
from pytz import UTC
from mangrove.datastore.field import TextField, IntegerField, SelectField, SelectField
from mangrove.datastore.form_model import FormModel
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined
from mangrove.datastore.datadict import DataDictType

def load_data():
    manager = get_db_manager()
    ENTITY_TYPE = ["Health_Facility", "Clinic"]
    FEB = datetime.datetime(2011, 02, 01, tzinfo=UTC)
    MARCH = datetime.datetime(2011, 03, 01, tzinfo=UTC)
    dd_types = {
        'beds': DataDictType(manager, name='beds', slug='beds', primitive_type='number'),
        'meds': DataDictType(manager, name='meds', slug='meds', primitive_type='number'),
        'patients': DataDictType(manager, name='patients', slug='patients', primitive_type='number'),
        'doctors': DataDictType(manager, name='doctors', slug='doctors', primitive_type='number'),
        'director': DataDictType(manager, name='director', slug='director', primitive_type='string')
    }
    for label, dd_type in dd_types.items():
        dd_type.save()
    define_type(manager, ["Health_Facility", "Clinic"])
    #  Default Entity Types
    try:
        define_type(manager, "Reporter")
    except EntityTypeAlreadyDefined:
        pass

    # Entities for State 1: Maharashtra
    e = Entity(manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Pune'], id="100")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Surgeon"])
    e.save()

    e.add_data(data=[("beds", 300, dd_types['beds']), ("meds", 20, dd_types['meds']),
                     ("director", "Dr. A", dd_types['director']), ("patients", 10, dd_types['patients'])],
               event_time=FEB)
    e.add_data(data=[("beds", 500, dd_types['beds']), ("meds", 20, dd_types['meds']),
                     ("patients", 20, dd_types['patients'])],
               event_time=MARCH)

    e = Entity(manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Pune'], id="200")
    e.set_aggregation_path("governance", ["Director", "Med_Supervisor", "Surgeon"])
    e.save()
    e.add_data(data=[("beds", 100, dd_types['beds']), ("meds", 10, dd_types['meds']),
                     ("director", "Dr. AA", dd_types['director']), ("patients", 50, dd_types['patients'])],
               event_time=FEB)
    e.add_data(data=[("beds", 200, dd_types['beds']), ("meds", 20, dd_types['meds']),
                     ("patients", 20, dd_types['patients'])],
               event_time=MARCH)

    e = Entity(manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Mumbai'], id="300")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Doctor"])
    e.save()
    e.add_data(data=[("beds", 100, dd_types['beds']), ("meds", 10, dd_types['meds']),
                     ("director", "Dr. AAA", dd_types['director']), ("patients", 50, dd_types['patients'])],
               event_time=FEB)
    e.add_data(data=[("beds", 200, dd_types['beds']), ("meds", 20, dd_types['meds']),
                     ("patients", 50, dd_types['patients'])],
               event_time=MARCH)

    # Entities for State 2: karnataka
    e = Entity(manager, entity_type=ENTITY_TYPE, location=['India', 'Karnataka', 'Bangalore'], id="400")
    e.set_aggregation_path("governance", ["Director", "Med_Supervisor", "Nurse"])
    e.save()
    e.add_data(data=[("beds", 100, dd_types['beds']), ("meds", 250, dd_types['meds']),
                     ("director", "Dr. B1", dd_types['director']), ("patients", 50, dd_types['patients'])],
               event_time=FEB)
    e.add_data(data=[("beds", 200, dd_types['beds']), ("meds", 400, dd_types['meds']),
                     ("director", "Dr. B2", dd_types['director']), ("patients", 20, dd_types['patients'])],
               event_time=MARCH)
    e = Entity(manager, entity_type=ENTITY_TYPE, location=['India', 'Karnataka', 'Hubli'])
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Surgeon"])
    e.save()
    e.add_data(data=[("beds", 100, dd_types['beds']), ("meds", 250, dd_types['meds']),
                     ("director", "Dr. B1", dd_types['director']), ("patients", 50, dd_types['patients'])],
               event_time=FEB)
    e.add_data(data=[("beds", 200, dd_types['beds']), ("meds", 400, dd_types['meds']),
                     ("director", "Dr. B2", dd_types['director']), ("patients", 20, dd_types['patients'])],
               event_time=MARCH)


    # Entities for State 3: Kerala
    e = Entity(manager, entity_type=ENTITY_TYPE, location=['India', 'Kerala', 'Kochi'], id="500")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    e.save()
    e.add_data(data=[("beds", 200, dd_types['beds']), ("meds", 50, dd_types['meds']),
                     ("director", "Dr. C", dd_types['director']), ("patients", 12, dd_types['patients'])],
               event_time=MARCH)


    question1 = TextField(name="entity_question", question_code="EID", label="What is associated entity"
                          , language="eng", entity_question_flag=True)
    question2 = TextField(name="question1_Name", question_code="Q1", label="What is your name",
                          defaultValue="some default value", language="eng")
    question3 = IntegerField(name="Father's age", question_code="Q2", label="What is your Father's Age",
                             range={"min": 15, "max": 120})

    form_model = FormModel(manager, entity_type_id="Health_Facility.Clinic", name="AIDS", label="Aids form_model",
                                form_code="QRID01", type='survey', fields=[
                    question1, question2, question3])
    form_model.save()



  
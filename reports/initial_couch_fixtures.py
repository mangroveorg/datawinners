# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
from mangrove.datastore.datarecord import register
from mangrove.datastore.entity import Entity, define_type
from mangrove.datastore.database import get_db_manager
from pytz import UTC
from mangrove.datastore.field import TextField, IntegerField, SelectField, SelectField
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined
from mangrove.form_model.form_model import FormModel

def define_entity_instance(manager, ENTITY_TYPE, location, id):
    return Entity(manager, entity_type=ENTITY_TYPE, location=location, id=id)

def load_data():
    manager = get_db_manager()
    ENTITY_TYPE = ["Health_Facility", "Clinic"]
    FEB = datetime.datetime(2011, 02, 01, tzinfo=UTC)
    MARCH = datetime.datetime(2011, 03, 01, tzinfo=UTC)

    #  Default Entity Types
    try:
        define_type(manager, "Reporter")
        define_type(manager, ["Health_Facility", "Clinic"])
    except EntityTypeAlreadyDefined:
        pass

    e = define_entity_instance(manager, ENTITY_TYPE, ['India', 'MH', 'Pune'], "100")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Surgeon"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 300), ("meds", 20), ("director", "Dr. A"), ("patients", 10)],
                   event_time=FEB)
        e.add_data(data=[("beds", 500), ("meds", 20), ("patients", 20)],
                   event_time=MARCH)

    e = define_entity_instance(manager, ENTITY_TYPE, ['India', 'MH', 'Pune'], "200")
    e.set_aggregation_path("governance", ["Director", "Med_Supervisor", "Surgeon"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 100), ("meds", 10), ("director", "Dr. AA"), ("patients", 50)],
                   event_time=FEB)
        e.add_data(data=[("beds", 200), ("meds", 20), ("patients", 20)],
                   event_time=MARCH)

    e = define_entity_instance(manager, ENTITY_TYPE, ['India', 'MH', 'Mumbai'], "300")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Doctor"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 100), ("meds", 10), ("director", "Dr. AAA"), ("patients", 50)],
               event_time=FEB)
        e.add_data(data=[("beds", 200), ("meds", 20), ("patients", 50)],
               event_time=MARCH)

    e = define_entity_instance(manager, ENTITY_TYPE, ['India', 'Karnataka', 'Bangalore'], "400")
    e.set_aggregation_path("governance", ["Director", "Med_Supervisor", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 100), ("meds", 250), ("director", "Dr. B1"), ("patients", 50)],
               event_time=FEB)
        e.add_data(data=[("beds", 200), ("meds", 400), ("director", "Dr. B2"), ("patients", 20)],
               event_time=MARCH)

    e = define_entity_instance(manager, ENTITY_TYPE, ['India', 'Kerala', 'Kochi'], "500")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except:
        pass
    else:
        e.add_data(data=[("beds", 200), ("meds", 50), ("director", "Dr. C"), ("patients", 12)],
               event_time=MARCH)

#
#    question1 = TextField(name="entity_question", question_code="EID", label="What is associated entity"
#                          , language="eng", entity_question_flag=True)
#    question2 = TextField(name="question1_Name", question_code="Q1", label="What is your name",
#                          defaultValue="some default value", language="eng")
#    question3 = IntegerField(name="Father's age", question_code="Q2", label="What is your Father's Age",
#                             range={"min": 15, "max": 120})
#
#    form_model = FormModel(manager, entity_type_id="Health_Facility.Clinic", name="AIDS", label="Aids form_model",
#                           form_code="QRID01", type='survey', fields=[
#                    question1, question2, question3])
#    form_model.save()


    #Register Reporter

    register(manager, entity_type=["Reporter"], data=[("telephone_number", "1234567890")], location=[],
                        source="sms")


  
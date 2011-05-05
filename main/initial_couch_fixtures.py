# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.datarecord import register
from mangrove.datastore.entity import Entity, define_type
from mangrove.datastore.database import get_db_manager
from pytz import UTC
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined
from mangrove.form_model.field import TextField, IntegerField
from mangrove.form_model.form_model import FormModel
from mangrove.form_model.validation import IntegerConstraint


def define_entity_instance(manager, ENTITY_TYPE, location, id):
    return Entity(manager, entity_type=ENTITY_TYPE, location=location, id=id)


def load_data():
    manager = get_db_manager()
    ENTITY_TYPE = ["Clinic"]
    ENTITY_TYPE2 = ["Water Point"]
    FEB = datetime.datetime(2011, 02, 01, tzinfo=UTC)
    MARCH = datetime.datetime(2011, 03, 01, tzinfo=UTC)

    #  The Default Entity Types
    try:
        define_type(manager, "Reporter")
        define_type(manager, "Clinic")
        define_type(manager, "Water Point")

    except EntityTypeAlreadyDefined:
        pass
    try:
        meds_type = DataDictType(manager, name='Medicines', slug='meds', primitive_type='number', description='Number of medications')
        beds_type = DataDictType(manager, name='Beds', slug='beds', primitive_type='number', description='Number of beds')
        director_type = DataDictType(manager, name='Director', slug='dir', primitive_type='string', description='Name of director')
        facility_type = DataDictType(manager, name='Facility', slug='facility', primitive_type='string', description='Name of facility')
        patients_type = DataDictType(manager, name='Patients', slug='patients', primitive_type='number', description='Patient Count')
        meds_type.save()
        beds_type.save()
        director_type.save()
        facility_type.save()
        patients_type.save()
    except Exception:
        pass

    e = define_entity_instance(manager, ENTITY_TYPE, ['India', 'MH', 'Pune'], "CID001")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Surgeon"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 300, beds_type), ("meds", 20, meds_type), ("director", "Dr. Donald Duck", director_type),
                         ("patients", 10, patients_type)],
                   event_time=FEB)
        e.add_data(data=[("beds", 500, beds_type), ("meds", 20, meds_type), ("patients", 20, patients_type)],
                   event_time=MARCH)

    e = define_entity_instance(manager, ENTITY_TYPE, ['India', 'MH', 'Pune'], "CID002")
    e.set_aggregation_path("governance", ["Director", "Med_Supervisor", "Surgeon"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 100, beds_type), ("meds", 10, meds_type), ("director", "Dr. Scrooge", director_type),
        ("patients", 50, patients_type)], event_time=FEB)
        e.add_data(data=[("beds", 200, beds_type), ("meds", 20, meds_type), ("patients", 20, patients_type)],
                   event_time=MARCH)

    e = define_entity_instance(manager, ENTITY_TYPE, ['India', 'MH', 'Mumbai'], "CID003")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Doctor"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 100, beds_type), ("meds", 10, meds_type), ("director", "Dr. Huey", director_type), ("patients", 50, patients_type)],
               event_time=FEB)
        e.add_data(data=[("beds", 200, beds_type), ("meds", 20, meds_type), ("patients", 50, patients_type)],
               event_time=MARCH)

    e = define_entity_instance(manager, ENTITY_TYPE, ['India', 'Karnataka', 'Bangalore'], "CID004")
    e.set_aggregation_path("governance", ["Director", "Med_Supervisor", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 100, beds_type), ("meds", 250, meds_type), ("director", "Dr. Dewey", director_type), ("patients", 50, patients_type)],
               event_time=FEB)
        e.add_data(data=[("beds", 200, beds_type), ("meds", 400, meds_type), ("director", "Dr. Louie", director_type), ("patients", 20, patients_type)],
               event_time=MARCH)

    e = define_entity_instance(manager, ENTITY_TYPE, ['India', 'Kerala', 'Kochi'], "CID005")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 200, beds_type), ("meds", 50, meds_type), ("director", "Dr. Glomgold", director_type), ("patients", 12, patients_type)],
               event_time=MARCH)
    e = define_entity_instance(manager, ENTITY_TYPE, ['India', 'Madhya Pradesh', 'New Gwalior'], "CID006")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 200, beds_type), ("meds", 50, meds_type), ("director", "Dr. Flintheart", director_type), ("patients", 12, patients_type)],
               event_time=MARCH)
    e = define_entity_instance(manager, ENTITY_TYPE, ['India', 'Madhya Pradesh', 'Bhopal'], "CID007")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 200, beds_type), ("meds", 50, meds_type), ("director", "Dr. Duck", director_type), ("patients", 12, patients_type)],
               event_time=MARCH)
    e = define_entity_instance(manager, ENTITY_TYPE2, ['India', 'Gujrat', 'Ahmedabad'], "WP01")
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass

    e = define_entity_instance(manager, ENTITY_TYPE2, ['India', 'Gujrat', 'Bhuj'], "WP02")
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass

    e = define_entity_instance(manager, ENTITY_TYPE2, ['India', 'Gujrat', 'Kacch'], "WP03")
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass
    question1 = TextField(name="entity_question", question_code="EID", label="What is associated entity"
                          , language="eng", entity_question_flag=True)
    question2 = TextField(name="Name", question_code="Q1", label="What is your name",
                          defaultValue="some default value", language="eng")
    question3 = IntegerField(name="Father's age", question_code="Q2", label="What is your Father's Age",
                             range=IntegerConstraint(min=15, max=120))

    form_model = FormModel(manager, entity_type_id="Clinic", name="AIDS", label="Aids form_model",
                           form_code="QRID01", type='survey', fields=[
                    question1, question2, question3])
    form_model.save()
    #Register Reporter
    phone_number_type = DataDictType(manager, name='Telephone Number', slug='telephone_number', primitive_type='string')
    first_name_type = DataDictType(manager, name='First Name', slug='first_name', primitive_type='string')
    phone_number_type.save()
    first_name_type.save()
    register(manager, entity_type=["Reporter"], data=[("telephone_number", "1234567890", phone_number_type), ("first_name", "Shweta", first_name_type)], location=[],
                        source="sms")

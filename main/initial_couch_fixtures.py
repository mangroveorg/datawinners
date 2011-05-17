# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
from datawinners.project.models import Project
from mangrove.datastore.datadict import DataDictType, create_ddtype, get_datadict_type_by_slug
from mangrove.datastore.datarecord import register
from mangrove.datastore.entity import Entity, define_type
from mangrove.datastore.database import get_db_manager
from pytz import UTC
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined, DataObjectAlreadyExists, DataObjectNotFound
from mangrove.form_model.field import TextField, IntegerField
from mangrove.form_model.form_model import FormModel, RegistrationFormModel
from mangrove.form_model.validation import NumericConstraint


def define_entity_instance(manager, ENTITY_TYPE, location, id):
    return Entity(manager, entity_type=ENTITY_TYPE, location=location, id=id)


def create_entity_types(manager, entity_types):
    for entity_type in entity_types:
        try:
            define_type(manager, entity_type)
        except EntityTypeAlreadyDefined:
            pass


def create_if_not_exists(create_fn, *args, **kwargs):
    try:
        return create_fn(*args, **kwargs)
    except DataObjectAlreadyExists:
        return None


def create_data_dict(dbm, name, slug, primitive_type, description=None):
    try:
        existing = get_datadict_type_by_slug(dbm, slug)
        existing.delete()
    except DataObjectNotFound:
        pass
    return create_ddtype(dbm, name, slug, primitive_type, description)


def load_data():
    manager = get_db_manager()
    CLINIC_ENTITY_TYPE = ["Clinic"]
    WATER_POINT_ENTITY_TYPE = ["Water Point"]
    REPORTER_ENTITY_TYPE = ["Reporter"]
    FEB = datetime.datetime(2011, 02, 01, tzinfo=UTC)
    MARCH = datetime.datetime(2011, 03, 01, tzinfo=UTC)

    #  The Default Entity Types
    create_entity_types(manager, [REPORTER_ENTITY_TYPE, CLINIC_ENTITY_TYPE, WATER_POINT_ENTITY_TYPE])

    #Data Dict Types
    meds_type = create_data_dict(dbm=manager, name='Medicines', slug='meds', primitive_type='number', description='Number of medications')
    beds_type = create_data_dict(dbm=manager, name='Beds', slug='beds', primitive_type='number', description='Number of beds')
    director_type = create_data_dict(dbm=manager, name='Director', slug='dir', primitive_type='string', description='Name of director')
    facility_type = create_data_dict(dbm=manager, name='Facility', slug='facility', primitive_type='string', description='Name of facility')
    patients_type = create_data_dict(dbm=manager, name='Patients', slug='patients', primitive_type='number', description='Patient Count')

    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MH', 'Pune'], "CID001")
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

    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MH', 'Pune'], "CID002")
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

    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MH', 'Mumbai'], "CID003")
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

    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Karnataka', 'Bangalore'], "CID004")
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

    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Kerala', 'Kochi'], "CID005")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 200, beds_type), ("meds", 50, meds_type), ("director", "Dr. Glomgold", director_type), ("patients", 12, patients_type)],
               event_time=MARCH)
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Madhya Pradesh', 'New Gwalior'], "CID006")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 200, beds_type), ("meds", 50, meds_type), ("director", "Dr. Flintheart", director_type), ("patients", 12, patients_type)],
               event_time=MARCH)
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Madhya Pradesh', 'Bhopal'], "CID007")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 200, beds_type), ("meds", 50, meds_type), ("director", "Dr. Duck", director_type), ("patients", 12, patients_type)],
               event_time=MARCH)
    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Gujrat', 'Ahmedabad'], "WP01")
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass

    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Gujrat', 'Bhuj'], "WP02")
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass

    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Gujrat', 'Kacch'], "WP03")
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass

    location_type = create_data_dict(manager, name='Location Type', slug='location', primitive_type='string')
    description_type = create_data_dict(manager, name='description Type', slug='description', primitive_type='string')
    mobile_number_type = create_data_dict(manager, name='Mobile Number Type', slug='mobile_number', primitive_type='string')
    name_type = create_data_dict(manager, name='Name', slug='Name', primitive_type='string')
    entity_id_type = create_data_dict(manager, name='Entity Id', slug='entity_id', primitive_type='string')
    age_type = create_data_dict(manager, name='Age Type', slug='age', primitive_type='integer')

    question1 = TextField(name="entity_question", question_code="EID", label="What is associated entity",
                          language="eng", entity_question_flag=True, ddtype=entity_id_type)
    question2 = TextField(name="Name", question_code="Q1", label="What is your name",
                          defaultValue="some default value", language="eng", ddtype=name_type)
    question3 = IntegerField(name="Father's age", question_code="Q2", label="What is your Father's Age",
                             range=NumericConstraint(min=15, max=120), ddtype=age_type)

    form_model = FormModel(manager, name="AIDS", label="Aids form_model",
                           form_code="QRID01", type='survey', fields=[
                    question1, question2, question3])
    qid = form_model.save()
    project = Project(name="Test_Project", goals="testing", project_type="survey", entity_type=CLINIC_ENTITY_TYPE, devices=["sms"])
    project.qid = qid
    try:
        project.save()
    except Exception:
        pass
    

    #Create registration questionnaire
    question1 = TextField(name="entity_type", question_code="T", label="What is associated entity type?",
                          language="eng", entity_question_flag=False, ddtype=entity_id_type)

    question2 = TextField(name="name", question_code="N", label="What is the entity's name?",
                          defaultValue="some default value", language="eng", ddtype=name_type)
    question3 = TextField(name="short_name", question_code="S", label="What is the entity's short name?",
                          defaultValue="some default value", language="eng", ddtype=name_type)
    question4 = TextField(name="location", question_code="L", label="What is the entity's location?",
                          defaultValue="some default value", language="eng", ddtype=location_type)
    question5 = TextField(name="description", question_code="D", label="Describe the entity",
                          defaultValue="some default value", language="eng", ddtype=description_type)
    question6 = TextField(name="mobile_number", question_code="M", label="What is the associated mobile number?",
                          defaultValue="some default value", language="eng", ddtype=mobile_number_type)
   
    form_model = RegistrationFormModel(manager, name="REG", form_code="REG", fields=[
                    question1, question2, question3, question4, question5, question6])
    qid = form_model.save()

    #Register Reporter
    phone_number_type = create_data_dict(manager, name='Telephone Number', slug='telephone_number', primitive_type='string')
    first_name_type = create_data_dict(manager, name='First Name', slug='first_name', primitive_type='string')
    register(manager, entity_type=["Reporter"], data=[("telephone_number", "1234567890", phone_number_type),
                                                      ("first_name", "Shweta", first_name_type)], location=[],
                        source="sms")

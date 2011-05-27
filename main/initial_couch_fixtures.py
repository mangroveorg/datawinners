# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
from django.contrib.auth.models import User
from datawinners import initializer
from datawinners.main.utils import get_database_manager_for_user
from datawinners.project.models import Project
from mangrove.datastore.datadict import create_datadict_type, get_datadict_type_by_slug
from mangrove.datastore.datarecord import register
from mangrove.datastore.entity import  define_type, create_entity
from pytz import UTC
from mangrove.datastore.reporter import REPORTER_ENTITY_TYPE
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined, DataObjectNotFound
from mangrove.form_model.field import TextField, IntegerField, DateField, SelectField
from mangrove.form_model.form_model import FormModel, NAME_FIELD, MOBILE_NUMBER_FIELD
from mangrove.form_model.validation import NumericConstraint, TextConstraint


def define_entity_instance(manager, entity_type, location, short_code, geometry):
    return create_entity(manager,entity_type=entity_type,location=location,aggregation_paths=None,short_code=short_code, geometry=geometry)


def create_entity_types(manager, entity_types):
    for entity_type in entity_types:
        try:
            define_type(manager, entity_type)
        except EntityTypeAlreadyDefined:
            pass


def create_data_dict(dbm, name, slug, primitive_type, description=None):
    try:
        existing = get_datadict_type_by_slug(dbm, slug)
        existing.delete()
    except DataObjectNotFound:
        pass
    return create_datadict_type(dbm, name, slug, primitive_type, description)


def load_manager_for_default_test_account():
    DEFAULT_USER = "tester150411@gmail.com"
    user = User.objects.get(username=DEFAULT_USER)
    return get_database_manager_for_user(user)


def load_data():
    manager = load_manager_for_default_test_account()
    initializer.run(manager)

    CLINIC_ENTITY_TYPE = ["Clinic"]
    WATER_POINT_ENTITY_TYPE = ["Water Point"]
    FEB = datetime.datetime(2011, 02, 01, tzinfo=UTC)
    MARCH = datetime.datetime(2011, 03, 01, tzinfo=UTC)

    #  The Default Entity Types
    create_entity_types(manager, [CLINIC_ENTITY_TYPE, WATER_POINT_ENTITY_TYPE])

    #Data Dict Types
    meds_type = create_data_dict(dbm=manager, name='Medicines', slug='meds', primitive_type='number',
                                 description='Number of medications')
    beds_type = create_data_dict(dbm=manager, name='Beds', slug='beds', primitive_type='number',
                                 description='Number of beds')
    director_type = create_data_dict(dbm=manager, name='Director', slug='dir', primitive_type='string',
                                     description='Name of director')
    patients_type = create_data_dict(dbm=manager, name='Patients', slug='patients', primitive_type='number',
                                     description='Patient Count')

    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MH', 'Pune'], short_code="CID001", geometry={"type": "Point", "coordinates": [73.3, 29.8]})
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Surgeon"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(
            data=[("beds", 300, beds_type), ("meds", 20, meds_type), ("director", "Dr. Donald Duck", director_type),
                  ("patients", 10, patients_type)],
            event_time=FEB)
        e.add_data(data=[("beds", 500, beds_type), ("meds", 20, meds_type), ("patients", 20, patients_type)],
                   event_time=MARCH)

    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MH', 'Pune'], short_code="CID002", geometry={"type": "Point", "coordinates": [76.3, 21.6]})
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

    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MH', 'Mumbai'], short_code="CID003", geometry={"type": "Point", "coordinates": [76.3, 23.8]})
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Doctor"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 100, beds_type), ("meds", 10, meds_type), ("director", "Dr. Huey", director_type),
                         ("patients", 50, patients_type)],
                   event_time=FEB)
        e.add_data(data=[("beds", 200, beds_type), ("meds", 20, meds_type), ("patients", 50, patients_type)],
                   event_time=MARCH)

    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Karnataka', 'Bangalore'], short_code="CID004", geometry={"type": "Point", "coordinates": [76.3, 12.8]})
    e.set_aggregation_path("governance", ["Director", "Med_Supervisor", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 100, beds_type), ("meds", 250, meds_type), ("director", "Dr. Dewey", director_type),
                         ("patients", 50, patients_type)],
                   event_time=FEB)
        e.add_data(data=[("beds", 200, beds_type), ("meds", 400, meds_type), ("director", "Dr. Louie", director_type),
                         ("patients", 20, patients_type)],
                   event_time=MARCH)

    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Kerala', 'Kochi'], short_code="CID005", geometry={"type": "Point", "coordinates": [79.3, 21.8]})
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 200, beds_type), ("meds", 50, meds_type), ("director", "Dr. Glomgold", director_type),
                         ("patients", 12, patients_type)],
                   event_time=MARCH)
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Madhya Pradesh', 'New Gwalior'],
                               short_code="CID006", geometry={"type": "Point", "coordinates": [71.3, 20.8]})
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(
            data=[("beds", 200, beds_type), ("meds", 50, meds_type), ("director", "Dr. Flintheart", director_type),
                  ("patients", 12, patients_type)],
            event_time=MARCH)
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Madhya Pradesh', 'Bhopal'], short_code="CID007", geometry={"type": "Point", "coordinates": [70.3, 18.8]})
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    else:
        e.add_data(data=[("beds", 200, beds_type), ("meds", 50, meds_type), ("director", "Dr. Duck", director_type),
                         ("patients", 12, patients_type)],
                   event_time=MARCH)
    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Gujrat', 'Ahmedabad'], short_code="WP01", geometry={"type": "Point", "coordinates": [76.3, 21.8]})
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass

    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Gujrat', 'Bhuj'], short_code="WP02", geometry={"type": "Point", "coordinates": [76.3, 25.3]})
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass

    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Gujrat', 'Kacch'], short_code="WP03", geometry={"type": "Point", "coordinates": [80.3, 21.6]})
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass

    name_type = create_data_dict(manager, name='Name', slug='Name', primitive_type='string')
    # Entity id is a default type in the system.
    entity_id_type = get_datadict_type_by_slug(manager, slug='entity_id')
    age_type = create_data_dict(manager, name='Age Type', slug='age', primitive_type='integer')
    date_type = create_data_dict(manager, name='Report Date', slug='date', primitive_type='date')
    select_type = create_data_dict(manager, name='Choice Type', slug='choice', primitive_type='select')

    question1 = TextField(label="entity_question", code="EID", name="What is associated entity?",
                          language="eng", entity_question_flag=True, ddtype=entity_id_type)
    question2 = TextField(label="Name", code="NA", name="What is your name?",
                          length=TextConstraint(min=1, max=10),
                          defaultValue="some default value", language="eng", ddtype=name_type)
    question3 = IntegerField(label="Father age", code="FA", name="What is age of father?",
                             range=NumericConstraint(min=18, max=100), ddtype=age_type)
    question4 = DateField(label="Report date", code="RD", name="What is reporting date?",
                          date_format="dd.mm.yyyy", ddtype=date_type)
    question5 = SelectField(label="Blood Group", code="BG", name="What is your blood group?",
                            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True,
                            ddtype=select_type)
    question6 = SelectField(label="Symptoms", code="SY", name="What are symptoms?",
                            options=[("Rapid weight loss", "a"), ("Dry cough", "b"), ("Pneumonia", "c"),
                                     ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False,
                            ddtype=select_type)

    form_model = FormModel(manager, name="AIDS", label="Aids form_model",
                           form_code="CLI001", type='survey',
                           fields=[question1, question2, question3, question4, question5, question6],
                           entity_type=CLINIC_ENTITY_TYPE
                           )
    qid = form_model.save()
    project = Project(name="Clinic Test Project", goals="This project is for automation", project_type="survey",
                      entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms"])
    project.qid = qid
    try:
        project.save(manager)
    except Exception:
        pass

    form_model2 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="CLI002", type='survey',
                            fields=[question1, question2, question3, question4, question5, question6],
                            entity_type=CLINIC_ENTITY_TYPE)
    qid2 = form_model2.save()
    project2 = Project(name="Clinic2 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web"])
    project2.qid = qid2
    try:
        project2.save(manager)
    except Exception:
        pass


    #Register Reporter
    phone_number_type = create_data_dict(manager, name='Telephone Number', slug='telephone_number',
                                         primitive_type='string')
    first_name_type = create_data_dict(manager, name='First Name', slug='first_name', primitive_type='string')
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "1234567890", phone_number_type),
                                                              (NAME_FIELD, "Shweta", first_name_type)], location=[],
             source="sms", short_code="REP1")

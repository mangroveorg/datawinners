# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
from django.contrib.auth.models import User
from datawinners import initializer
from datawinners.main.utils import get_database_manager_for_user
from datawinners.project.models import Project
from datawinners.submission.views import SMS
from mangrove.datastore.datadict import create_datadict_type, get_datadict_type_by_slug
from mangrove.datastore.entity import  define_type, create_entity
from pytz import UTC
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined, DataObjectNotFound
from mangrove.form_model.field import TextField, IntegerField, DateField, SelectField, GeoCodeField
from mangrove.form_model.form_model import FormModel, NAME_FIELD, MOBILE_NUMBER_FIELD
from mangrove.form_model.validation import NumericConstraint, TextConstraint
from mangrove.transport.player.player import Request, SMSPlayer
from mangrove.transport.reporter import REPORTER_ENTITY_TYPE
from mangrove.transport.submissions import SubmissionHandler


def define_entity_instance(manager, entity_type, location, short_code, geometry):
    return create_entity(manager, entity_type=entity_type, location=location, aggregation_paths=None,
                         short_code=short_code, geometry=geometry)


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


def register(manager, entity_type, data, location, short_code):
    e = create_entity(manager, entity_type=entity_type, location=location, aggregation_paths=None,
                      short_code=short_code)
    e.add_data(data=data)
    return e


def load_datadict_types(manager):
    meds_type = create_data_dict(dbm=manager, name='Medicines', slug='meds', primitive_type='number',
                                 description='Number of medications')
    beds_type = create_data_dict(dbm=manager, name='Beds', slug='beds', primitive_type='number',
                                 description='Number of beds')
    director_type = create_data_dict(dbm=manager, name='Director', slug='dir', primitive_type='string',
                                     description='Name of director')
    patients_type = create_data_dict(dbm=manager, name='Patients', slug='patients', primitive_type='geocode',
                                     description='Patient Count')


def load_clinic_entities(CLINIC_ENTITY_TYPE, manager):
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MH', 'Pune'], short_code="cid001",
                               geometry={"type": "Point", "coordinates": [73.8567437, 18.5204303]})
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Surgeon"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MH', 'Pune'], short_code="cid002",
                               geometry={"type": "Point", "coordinates": [73.8567437, 18.5204303]})
    e.set_aggregation_path("governance", ["Director", "Med_Supervisor", "Surgeon"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MH', 'Mumbai'], short_code="cid003",
                               geometry={"type": "Point", "coordinates": [72.856164, 19.017615]})
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Doctor"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Karnataka', 'Bangalore'], short_code="cid004",
                               geometry={"type": "Point", "coordinates": [77.594563, 12.971599]})
    e.set_aggregation_path("governance", ["Director", "Med_Supervisor", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Kerala', 'Kochi'], short_code="cid005",
                               geometry={"type": "Point", "coordinates": [76.259625, 9.939248]})
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Madhya Pradesh', 'New Gwalior'],
                               short_code="cid006", geometry={"type": "Point", "coordinates": [78.18708, 26.227112]})
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Madhya Pradesh', 'Bhopal'], short_code="cid007",
                               geometry={"type": "Point", "coordinates": [77.412615, 23.2599333]})
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass


def load_waterpoint_entities(WATER_POINT_ENTITY_TYPE, manager):
    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Gujrat', 'Ahmedabad'], short_code="wp01",
                               geometry={"type": "Point", "coordinates": [72.566005, 23.0395677]})
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Gujrat', 'Bhuj'], short_code="wp02",
                               geometry={"type": "Point", "coordinates": [69.66256, 23.251671]})
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Haryana', 'Gurgaon'], short_code="wp03",
                               geometry={"type": "Point", "coordinates": [77.017838, 28.46385]})
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass


def create_clinic_projects(CLINIC_ENTITY_TYPE, manager):
    name_type = create_data_dict(manager, name='Name', slug='Name', primitive_type='string')
    # Entity id is a default type in the system.
    entity_id_type = get_datadict_type_by_slug(manager, slug='entity_id')
    age_type = create_data_dict(manager, name='Age Type', slug='age', primitive_type='integer')
    date_type = create_data_dict(manager, name='Report Date', slug='date', primitive_type='date')
    select_type = create_data_dict(manager, name='Choice Type', slug='choice', primitive_type='select')
    geocode_type = create_data_dict(manager, name='Geocode Type', slug='choice', primitive_type='')
    question1 = TextField(label="entity_question", code="EID", name="What is associated entity?",
                          language="eng", entity_question_flag=True, ddtype=entity_id_type,
                          length=TextConstraint(min=1, max=12))
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
    question7 = GeoCodeField(label="Location", code="GC", name="What is your current location", ddtype=geocode_type)
    form_model = FormModel(manager, name="AIDS", label="Aids form_model",
                           form_code="cli001", type='survey',
                           fields=[question1, question2, question3, question4, question5, question6, question7],
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
                            form_code="cli002", type='survey',
                            fields=[question1, question2, question3, question4, question5, question6, question7],
                            entity_type=CLINIC_ENTITY_TYPE)
    qid2 = form_model2.save()
    project2 = Project(name="Clinic2 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web"])
    project2.qid = qid2
    try:
        project2.save(manager)
    except Exception:
        pass


def load_sms_data_for_cli001(manager):
    sms_player = SMSPlayer(manager, SubmissionHandler(manager))
    FROM_NUMBER = '1234567890'
    FROM_NUMBER = '1234567890'
    TO_NUMBER = '261333782943'
    message1 = "cli001 +EID cid001 +NA Mr. Tessy +FA 58 +RD 17.05.2011 +BG b +SY ade +GC 79.2 23.3"
    response = sms_player.accept(Request(transport=SMS, message=message1, source=FROM_NUMBER, destination=TO_NUMBER))
    message1 = "cli001 +EID cid002 +NA Mr. Adam +FA 62 +RD 17.04.2011 +BG a +SY ab +GC 74.2 23.3"
    response = sms_player.accept(Request(transport=SMS, message=message1, source=FROM_NUMBER, destination=TO_NUMBER))
    message1 = "cli001 +EID cid003 +NA Ms. Beth +FA 75 +RD 17.05.2011 +BG b +SY bc +GC 81.2 29.3"
    response = sms_player.accept(Request(transport=SMS, message=message1, source=FROM_NUMBER, destination=TO_NUMBER))
    message1 = "cli001 +EID cid004 +NA Thomas +FA 85 +RD 5.01.2011 +BG a +SY bd +GC 43.2 28.3"
    response = sms_player.accept(Request(transport=SMS, message=message1, source=FROM_NUMBER, destination=TO_NUMBER))
    message1 = "cli001 +EID cid005 +NA Ms. Beth +FA 62 +RD 12.02.2011 +BG d +SY bc +GC 81.2 29.3"
    response = sms_player.accept(Request(transport=SMS, message=message1, source=FROM_NUMBER, destination=TO_NUMBER))
    message1 = "cli001 +EID cid006 +NA Juannita +FA 86 +RD 5.02.2011 +BG c +SY ace +GC 41.2 29.3"
    response = sms_player.accept(Request(transport=SMS, message=message1, source=FROM_NUMBER, destination=TO_NUMBER))
    message1 = "cli001 +EID cid001 +NA Amanda +FA 16 +RD 5.02.2011 +BG c +SY ace +GC 41.2 29.3"
    response = sms_player.accept(Request(transport=SMS, message=message1, source=FROM_NUMBER, destination=TO_NUMBER))
    message1 = "cli001 +EID cid002 +NA Amanda +FA 16 +RD 5.02.2011 +BG e"
    response = sms_player.accept(Request(transport=SMS, message=message1, source=FROM_NUMBER, destination=TO_NUMBER))

def load_data():
    manager = load_manager_for_default_test_account()
    initializer.run(manager)
    CLINIC_ENTITY_TYPE = ["Clinic"]
    WATER_POINT_ENTITY_TYPE = ["Water Point"]
    FEB = datetime.datetime(2011, 02, 01, tzinfo=UTC)
    MARCH = datetime.datetime(2011, 03, 01, tzinfo=UTC)
    create_entity_types(manager, [CLINIC_ENTITY_TYPE, WATER_POINT_ENTITY_TYPE])
    load_datadict_types(manager)
    load_clinic_entities(CLINIC_ENTITY_TYPE, manager)
    load_waterpoint_entities(WATER_POINT_ENTITY_TYPE, manager)
    create_clinic_projects(CLINIC_ENTITY_TYPE, manager)

    #Register Reporter
    phone_number_type = create_data_dict(manager, name='Telephone Number', slug='telephone_number',
                                         primitive_type='string')
    first_name_type = create_data_dict(manager, name='First Name', slug='first_name', primitive_type='string')
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "1234567890", phone_number_type),
                                                              (NAME_FIELD, "Shweta", first_name_type)], location=[],
             short_code="REP1")
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "261332592634", phone_number_type),
                                                              (NAME_FIELD, "David", first_name_type)], location=[],
             short_code="REP2")

    load_sms_data_for_cli001(manager)
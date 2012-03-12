from django.contrib.auth.models import User, Group
from django.utils.translation import activate
from datawinners.common.constant import DEFAULT_LANGUAGE
from datawinners import initializer
from datawinners.accountmanagement.models import Organization

from datawinners.entity.helper import create_registration_form
from datawinners.main.utils import get_database_manager
from datawinners.project.models import Project, ProjectState, Reminder
from mangrove.datastore.datadict import create_datadict_type, get_datadict_type_by_slug
from mangrove.datastore.entity import  create_entity, get_by_short_code
from mangrove.datastore.entity_type import define_type
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined, DataObjectNotFound, DataObjectAlreadyExists
from mangrove.form_model.field import TextField, IntegerField, DateField
from mangrove.form_model.form_model import FormModel, NAME_FIELD, MOBILE_NUMBER_FIELD, DESCRIPTION_FIELD, get_form_model_by_code
from mangrove.form_model.validation import TextLengthConstraint, NumericRangeConstraint
from mangrove.transport.reporter import REPORTER_ENTITY_TYPE


FIRST_NAME_FIELD = "firstname"

def load_data():
    manager = load_manager_for_default_test_account()
    initializer.run(manager)
    PACKAGING_LIST_ENTITY_TYPE = [u"packaginglist"]
    create_entity_types(manager, [PACKAGING_LIST_ENTITY_TYPE])
    load_datadict_types(manager)
    load_packaginglist_entities(PACKAGING_LIST_ENTITY_TYPE, manager)
    create_waybill_sent_received_project(PACKAGING_LIST_ENTITY_TYPE, manager)
    #Register Reporters
    phone_number_type = create_data_dict(manager, name='Telephone Number', slug='telephone_number',
        primitive_type='string')
    first_name_type = create_data_dict(manager, name='First Name', slug='first_name', primitive_type='string')
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "919970059125", phone_number_type),
        (NAME_FIELD, "test", first_name_type)],
        location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
        short_code="rep5", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})


def load_manager_for_default_test_account():
    DEFAULT_USER = "tester150411@gmail.com"
    user = User.objects.get(username=DEFAULT_USER)
    group = Group.objects.filter(name="NGO Admins")
    user.groups.add(group[0])
    return get_database_manager(user)


def create_entity_types(manager, entity_types):
    for entity_type in entity_types:
        try:
            define_type(manager, entity_type)
            activate(DEFAULT_LANGUAGE)
            create_registration_form(manager, entity_type)
        except EntityTypeAlreadyDefined:
            pass


#Data Dict Types
def load_datadict_types(manager):
    meds_type = create_data_dict(dbm=manager, name='Medicines', slug='meds', primitive_type='number',
        description='Number of medications')
    beds_type = create_data_dict(dbm=manager, name='Beds', slug='beds', primitive_type='number',
        description='Number of beds')
    director_type = create_data_dict(dbm=manager, name='Director', slug='dir', primitive_type='string',
        description='Name of director')
    patients_type = create_data_dict(dbm=manager, name='Patients', slug='patients', primitive_type='geocode',
        description='Patient Count')


def create_data_dict(dbm, name, slug, primitive_type, description=None):
    try:
        existing = get_datadict_type_by_slug(dbm, slug)
        existing.delete()
    except DataObjectNotFound:
        pass
    return create_datadict_type(dbm, name, slug, primitive_type, description)


def load_packaginglist_entities(PACKAGING_LIST_ENTITY_TYPE, manager):
    e = define_entity_instance(manager, PACKAGING_LIST_ENTITY_TYPE, ['India', 'MP', 'Bhopal'], short_code="pac1",
        geometry={"type": "Point", "coordinates": [23.2833, 77.35]},
        name="Test", firstname="Bhopal Clinic", description="This a clinic in Bhopal.", mobile_number="123456")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Surgeon"])
    try:
        e.save()
    except Exception:
        pass


def define_entity_instance(manager, entity_type, location, short_code, geometry, name=None, mobile_number=None,
                           description=None, firstname=None):
    e = create_or_update_entity(manager, entity_type=entity_type, location=location, aggregation_paths=None,
        short_code=short_code, geometry=geometry)

    name_type = create_data_dict(manager, name='Name Type', slug='name', primitive_type='string')
    first_name_type = create_data_dict(manager, name='Name Type', slug='firstname', primitive_type='string')
    mobile_type = create_data_dict(manager, name='Mobile Number Type', slug='mobile_number', primitive_type='string')
    description_type = create_data_dict(manager, name='Description', slug='description', primitive_type='string')
    e.add_data(data=[(NAME_FIELD, name, name_type)])
    e.add_data([(FIRST_NAME_FIELD, firstname, first_name_type)])
    e.add_data([(MOBILE_NUMBER_FIELD, mobile_number, mobile_type)])
    e.add_data([(DESCRIPTION_FIELD, description, description_type)])
    return e


def create_or_update_entity(manager, entity_type, location, aggregation_paths, short_code, geometry=None):
    try:
        entity = get_by_short_code(manager, short_code, entity_type)
        entity.delete()
    except DataObjectNotFound:
        pass
    return create_entity(manager, entity_type, short_code, location, aggregation_paths, geometry)


def register(manager, entity_type, data, location, short_code, geometry=None):
    e = create_or_update_entity(manager, entity_type=entity_type, location=location, aggregation_paths=None,
        short_code=short_code, geometry=geometry)
    e.add_data(data=data)
    return e


def create_waybill_sent_received_project(PACKAGING_LIST_ENTITY_TYPE, manager):
    organization = Organization.objects.get(pk='SLX364903')
    Reminder.objects.filter(organization=organization).delete()
    name_type = create_data_dict(manager, name='Name', slug='Name', primitive_type='string')
    # Entity id is a default type in the system.
    weight_type = create_data_dict(manager, name='Weight Type', slug='weight', primitive_type='integer')
    entity_id_type = get_datadict_type_by_slug(manager, slug='entity_id')
    date_type = create_data_dict(manager, name='Report Date', slug='date', primitive_type='date')
    question1 = TextField(label="Which packaging list are you reporting on??", code="q1",
        name="Which packaging list are you reporting on?",
        language="en", entity_question_flag=True, ddtype=entity_id_type,
        constraints=[TextLengthConstraint(min=1, max=12)],
        instruction="Answer must be a word or phrase 12 characters maximum")
    question2 = TextField(label="What is the waybill code?", code="q2", name="What is the waybill code?",
        constraints=[TextLengthConstraint(min=1, max=10)],
        defaultValue="some default value", language="en", ddtype=name_type,
        instruction="Answer must be a word or phrase 10 characters maximum")
    question3 = DateField(label="Date of sending?", code="q3", name="Date of sending?",
        date_format="dd.mm.yyyy", ddtype=date_type,
        instruction="Answer must be a date in the following format: day.month.year. Example: 25.12.2011",
        event_time_field_flag=True)
    question4 = TextField(label="What is the Type of transaction?", code="q4", name="What is the Type of transaction?",
        constraints=[TextLengthConstraint(min=1, max=10)],
        defaultValue="some default value", language="en", ddtype=name_type,
        instruction="Answer must be a word or phrase 10 characters maximum")
    question5 = TextField(label="What is the Warehouse Code?", code="q5", name="What is the Warehouse Code?",
        constraints=[TextLengthConstraint(min=1, max=10)],
        defaultValue="some default value", language="en", ddtype=name_type,
        instruction="Answer must be a word or phrase 10 characters maximum")
    question6 = TextField(label="Name of Sender?", code="q6", name="Name of Sender?",
        constraints=[TextLengthConstraint(min=1, max=10)],
        defaultValue="some default value", language="en", ddtype=name_type,
        instruction="Answer must be a word or phrase 10 characters maximum")
    question7 = TextField(label="What is the Truck Id?", code="q7", name="What is the Truck Id?",
        constraints=[TextLengthConstraint(min=1, max=10)],
        defaultValue="some default value", language="en", ddtype=name_type,
        instruction="Answer must be a word or phrase 10 characters maximum")
    question8 = TextField(label="What is the Food Type?", code="q8", name="What is the Food Type?",
        constraints=[TextLengthConstraint(min=1, max=10)],
        defaultValue="some default value", language="en", ddtype=name_type,
        instruction="Answer must be a word or phrase 10 characters maximum")
    question9 = IntegerField(label="What is the Net Weight?", code="q9", name="What is the Net Weight?",
        constraints=[NumericRangeConstraint(min=18, max=10000)], ddtype=weight_type,
        instruction="Answer must be a number between 18-100.")

    form_model = FormModel(manager, name="WAYBILL_SENT", label="WAYBILL form_model",
        form_code="WBS01", type='survey',
        fields=[question1, question2, question3, question4, question5, question6, question7,
                question8, question9],
        entity_type=PACKAGING_LIST_ENTITY_TYPE
    )

    try:
        qid = form_model.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "WBS01").delete()
        qid = form_model.save()
    project1 = Project(name="Way Bill Sent", goals="This project is for automation", project_type="survey",
        entity_type=PACKAGING_LIST_ENTITY_TYPE[-1], devices=["sms", "web"], activity_report='no', sender_group="close")
    project1.qid = qid
    project1.state = ProjectState.ACTIVE
    try:
        project1.save(manager)
    except Exception:
        pass

    # Associate datasenders/reporters with project 1
    project1.data_senders.extend(["rep5"])
    project1.save(manager)

    question1 = TextField(label="Which packaging list are you reporting on??", code="q1",
        name="Which packaging list are you reporting on?",
        language="en", entity_question_flag=True, ddtype=entity_id_type,
        constraints=[TextLengthConstraint(min=1, max=12)],
        instruction="Answer must be a word or phrase 12 characters maximum")
    question2 = TextField(label="What is the waybill code?", code="q2", name="What is the waybill code?",
        constraints=[TextLengthConstraint(min=1, max=10)],
        defaultValue="some default value", language="en", ddtype=name_type,
        instruction="Answer must be a word or phrase 10 characters maximum")
    question3 = TextField(label="What is the Warehouse Code?", code="q3", name="What is the Warehouse Code?",
        constraints=[TextLengthConstraint(min=1, max=10)],
        defaultValue="some default value", language="en", ddtype=name_type,
        instruction="Answer must be a word or phrase 10 characters maximum")
    question4 = TextField(label="Name of Receiver?", code="q4", name="Name of Receiver?",
        constraints=[TextLengthConstraint(min=1, max=10)],
        defaultValue="some default value", language="en", ddtype=name_type,
        instruction="Answer must be a word or phrase 10 characters maximum")
    question5 = DateField(label="Date of receipt?", code="q5", name="Date of receipt?",
        date_format="dd.mm.yyyy", ddtype=date_type,
        instruction="Answer must be a date in the following format: day.month.year. Example: 25.12.2011",
        event_time_field_flag=True)
    question6 = TextField(label="What is the Truck Id?", code="q6", name="What is the Truck Id?",
        constraints=[TextLengthConstraint(min=1, max=10)],
        defaultValue="some default value", language="en", ddtype=name_type,
        instruction="Answer must be a word or phrase 10 characters maximum")
    question7 = IntegerField(label="What is the Good Weight?", code="q7", name="What is the Good Weight?",
        constraints=[NumericRangeConstraint(min=18, max=10000)], ddtype=weight_type,
        instruction="Answer must be a number between 18-100.")
    question8 = IntegerField(label="What is the Net Weight?", code="q8", name="What is the Net Weight?",
        constraints=[NumericRangeConstraint(min=18, max=10000)], ddtype=weight_type,
        instruction="Answer must be a number between 18-100.")


    form_model = FormModel(manager, name="WAYBILL_RECEIVED", label="WAYBILL form_model",
        form_code="WBR01", type='survey',
        fields=[question1, question2, question3, question4, question5, question6, question7,
                question8],
        entity_type=PACKAGING_LIST_ENTITY_TYPE
    )

    try:
        qid = form_model.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "WBR01").delete()
        qid = form_model.save()
    project2 = Project(name="Way Bill Received", goals="This project is for automation", project_type="survey",
        entity_type=PACKAGING_LIST_ENTITY_TYPE[-1], devices=["sms", "web"], activity_report='no', sender_group="close")
    project2.qid = qid
    project2.state = ProjectState.ACTIVE
    try:
        project2.save(manager)
    except Exception:
        pass

    # Associate datasenders/reporters with project 1
    project2.data_senders.extend(["rep5"])
    project2.save(manager)




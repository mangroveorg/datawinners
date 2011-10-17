# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import datetime, timedelta
from django.contrib.auth.models import User, Group
from mock import patch
from datawinners import initializer, settings
from datawinners.accountmanagement.models import OrganizationSetting, Organization
from datawinners.location.LocationTree import get_location_tree
from datawinners.main.utils import get_database_manager
from datawinners.project.models import Project, ProjectState, Reminder, RemindTo, ReminderMode
from datawinners.submission.views import SMS
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.datadict import create_datadict_type, get_datadict_type_by_slug
from mangrove.datastore.documents import attributes
from mangrove.datastore.entity import  create_entity, get_by_short_code
from pytz import UTC
from mangrove.datastore.entity_type import define_type
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined, DataObjectNotFound, DataObjectAlreadyExists
from mangrove.form_model.field import TextField, IntegerField, DateField, SelectField, GeoCodeField
from mangrove.form_model.form_model import FormModel, NAME_FIELD, MOBILE_NUMBER_FIELD, DESCRIPTION_FIELD, get_form_model_by_code, GEO_CODE_FIELD
from mangrove.form_model.validation import NumericRangeConstraint, TextLengthConstraint
from mangrove.transport.player.player import Request, SMSPlayer, TransportInfo
from mangrove.transport.reporter import REPORTER_ENTITY_TYPE
from mangrove.transport.submissions import Submission


class DateTimeMocker(object):
    def __init__(self):
        self.datetime_patcher = patch("mangrove.datastore.entity.utcnow")
        self.submission_date_patcher = patch("mangrove.datastore.documents.utcnow")
        self.submission_date_mock = self.submission_date_patcher.start()
        self.datetime_mock = self.datetime_patcher.start()

    def set_date_time_now(self, val):
        self.datetime_mock.return_value = val
        self.submission_date_mock.return_value = val

    def end_mock(self):
        self.datetime_patcher.stop()
        self.submission_date_patcher.stop()


def create_or_update_entity(manager, entity_type, location, aggregation_paths, short_code, geometry=None):
    try:
        entity = get_by_short_code(manager, short_code, entity_type)
        entity.delete()
    except DataObjectNotFound:
        pass
    return create_entity(manager, entity_type, short_code, location, aggregation_paths, geometry)


def define_entity_instance(manager, entity_type, location, short_code, geometry, name=None, mobile_number=None,
                           description=None):
    e = create_or_update_entity(manager, entity_type=entity_type, location=location, aggregation_paths=None,
                                short_code=short_code, geometry=geometry)
    name_type = create_data_dict(manager, name='Name Type', slug='Name', primitive_type='string')
    mobile_type = create_data_dict(manager, name='Mobile Number Type', slug='mobile_number', primitive_type='string')
    description_type = create_data_dict(manager, name='Description', slug='description', primitive_type='string')
    e.add_data(data=[(NAME_FIELD, name, name_type)])
    e.add_data([(MOBILE_NUMBER_FIELD, mobile_number, mobile_type)])
    e.add_data([(DESCRIPTION_FIELD, description, description_type)])
    return e


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
    group = Group.objects.filter(name="NGO Admins")
    user.groups.add(group[0])
    return get_database_manager(user)


def register(manager, entity_type, data, location, short_code, geometry=None):
    e = create_or_update_entity(manager, entity_type=entity_type, location=location, aggregation_paths=None,
                                short_code=short_code, geometry=geometry)
    e.add_data(data=data)
    return e

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


def load_clinic_entities(CLINIC_ENTITY_TYPE, manager):
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MP', 'Bhopal'], short_code="cid001",
                               geometry={"type": "Point", "coordinates": [23.2833, 77.35]},
                               name="Bhopal Clinic", description="This a clinic in Bhopal.", mobile_number="123456")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Surgeon"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MP', 'Satna'], short_code="cid002",
                               geometry={"type": "Point", "coordinates": [24.5667, 80.8333]},
                               name="Satna Clinic", description="This a clinic in Satna.", mobile_number="123457")
    e.set_aggregation_path("governance", ["Director", "Med_Supervisor", "Surgeon"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MP', 'Jabalpur'], short_code="cid003",
                               geometry={"type": "Point", "coordinates": [23.2, 79.95]},
                               name="Jabalpur Clinic", description="This a clinic in Jabalpur.", mobile_number="123458")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Doctor"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MP', 'Khandwa'], short_code="cid004",
                               geometry={"type": "Point", "coordinates": [21.8333, 76.3667]},
                               name="Khandwa Clinic", description="This a clinic in Khandwa.", mobile_number="123459")
    e.set_aggregation_path("governance", ["Director", "Med_Supervisor", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Kerala', 'Kochi'], short_code="cid005",
                               geometry={"type": "Point", "coordinates": [9.939248, 76.259625]},
                               name="Kochi Clinic", description="This a clinic in Kochi.", mobile_number="123460")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Madhya Pradesh', 'New Gwalior'],
                               short_code="cid006", geometry={"type": "Point", "coordinates": [26.227112, 78.18708]},
                               name="New Gwalior Clinic", description="This a clinic in New Gwalior.",
                               mobile_number="1234561")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Madhya Pradesh', 'Indore'], short_code="cid007",
                               geometry={"type": "Point", "coordinates": [22.7167, 75.8]},
                               name="Indore Clinic", description="This a clinic in Indore.", mobile_number="1234562")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass


def load_waterpoint_entities(WATER_POINT_ENTITY_TYPE, manager):
    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Gujrat', 'Ahmedabad'], short_code="wp01",
                               geometry={"type": "Point", "coordinates": [23.0395677, 72.566005]},
                               name="Ahmedabad waterpoint", description="This a waterpoint in Ahmedabad.",
                               mobile_number="1234563")
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Gujrat', 'Bhuj'], short_code="wp02",
                               geometry={"type": "Point", "coordinates": [23.251671, 69.66256]},
                               name="Bhuj waterpoint", description="This a waterpoint in Bhuj.",
                               mobile_number="1234564")
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Haryana', 'Gurgaon'], short_code="wp03",
                               geometry={"type": "Point", "coordinates": [28.46385, 77.017838]},
                               name="Gurgaon waterpoint", description="This a waterpoint in Gurgaon.",
                               mobile_number="1234564")
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass


def create_clinic_projects(CLINIC_ENTITY_TYPE, manager):
    organization = Organization.objects.get(pk='SLX364903')
    Reminder.objects.filter(organization = organization).delete()
    name_type = create_data_dict(manager, name='Name', slug='Name', primitive_type='string')
    # Entity id is a default type in the system.
    entity_id_type = get_datadict_type_by_slug(manager, slug='entity_id')
    age_type = create_data_dict(manager, name='Age Type', slug='age', primitive_type='integer')
    date_type = create_data_dict(manager, name='Report Date', slug='date', primitive_type='date')
    select_type = create_data_dict(manager, name='Choice Type', slug='choice', primitive_type='select')
    geo_code_type = create_data_dict(manager, name='GeoCode Type', slug='geo_code', primitive_type='geocode')
    question1 = TextField(label="entity_question", code="EID", name="What is associatéd entity?",
                          language="en", entity_question_flag=True, ddtype=entity_id_type,
                          constraints=[TextLengthConstraint(min=1, max=12)],
                          instruction="Answer must be a word or phrase 12 characters maximum")
    question2 = TextField(label="Name", code="NA", name="What is your namé?",
                          constraints=[TextLengthConstraint(min=1, max=10)],
                          defaultValue="some default value", language="en", ddtype=name_type,
                          instruction="Answer must be a word or phrase 10 characters maximum")
    question3 = IntegerField(label="Father age", code="FA", name="What is age öf father?",
                             constraints=[NumericRangeConstraint(min=18, max=100)], ddtype=age_type,
                             instruction="Answer must be a number between 18-100.")
    question4 = DateField(label="Report date", code="RD", name="What is réporting date?",
                          date_format="dd.mm.yyyy", ddtype=date_type,
                          instruction="Answer must be a date in the following format: day.month.year. Example: 25.12.2011")
    question5 = SelectField(label="Blood Group", code="BG", name="What is your blood group?",
                            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True,
                            ddtype=select_type, instruction="Choose 1 answer from the list.")
    question6 = SelectField(label="Symptoms", code="SY", name="What aré symptoms?",
                            options=[("Rapid weight loss", "a"), ("Dry cough", "b"), ("Pneumonia", "c"),
                                    ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False,
                            ddtype=select_type,
                            instruction="Choose 1 or more answers from the list.")
    question7 = GeoCodeField(name="What is the GPS codé for clinic", code="GPS",
                             label="What is the GPS code for clinic?",
                             language="en", ddtype=geo_code_type,
                             instruction="Answer must be GPS co-ordinates in the following format: xx.xxxx yy.yyyy Example: -18.1324 27.6547")
    question8 = SelectField(label="Required Medicines", code="RM", name="What are the required medicines?",
                            options=[("Hivid", "a"), ("Rétrovir", "b"), ("Vidéx EC", "c"), ("Epzicom", "d")],
                            single_select_flag=False,
                            ddtype=select_type,
                            instruction="Choose 1 or more answers from the list.", required=False)
    form_model = FormModel(manager, name="AIDS", label="Aids form_model",
                           form_code="cli001", type='survey',
                           fields=[question1, question2, question3, question4, question5, question6, question7,
                                   question8],
                           entity_type=CLINIC_ENTITY_TYPE
    )

    weekly_reminder_and_deadline = {
            "reminders_enabled": "True",
            "deadline_week": "5",
            "deadline_type": "That",
            "frequency_enabled": "True",
            "has_deadline": "True",
            "frequency_period": "week"
        }

    try:
        qid = form_model.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli001").delete()
        qid = form_model.save()
    project1 = Project(name="Clinic Test Project", goals="This project is for automation", project_type="survey",
                      entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web"], activity_report='no', sender_group="close",
                      reminder_and_deadline=weekly_reminder_and_deadline)
    project1.qid = qid
    project1.state = ProjectState.ACTIVE
    try:
        project1.save(manager)
    except Exception:
        pass

    # Create reminders for project1
    reminder = Reminder(project_id = project1.id,day=1,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "1 day is remainning to deadline. Please send your data for Clinic Test Project.")
    reminder.save()

    # Create reminders for project1
    reminder = Reminder(project_id = project1.id,day=2,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "2 days are remainning to deadline. Please send your data for Clinic Test Project.")
    reminder.save()

    # Create reminders for project1
    reminder = Reminder(project_id = project1.id,day=3,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "3 days are remainning to deadline. Please send your data for Clinic Test Project.")
    reminder.save()

    # Create reminders for project1
    reminder = Reminder(project_id = project1.id,day=4,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "4 days are remainning to deadline. Please send your data for Clinic Test Project.")
    reminder.save()

    # Create reminders for project1
    reminder = Reminder(project_id = project1.id,day=5,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "5 days are remainning to deadline. Please send your data for Clinic Test Project.")
    reminder.save()

    # Create reminders for project1
    reminder = Reminder(project_id = project1.id,day=0,reminder_mode=ReminderMode.ON_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "Today is the deadline. Please send your data for Clinic Test Project.")
    reminder.save()

    # Create reminders for project1
    reminder = Reminder(project_id = project1.id,day=1,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "1 day is overdue the deadline. Please send your data for Clinic Test Project.")
    reminder.save()

    # Create reminders for project1
    reminder = Reminder(project_id = project1.id,day=2,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "2 days are overdue the deadline. Please send your data for Clinic Test Project.")
    reminder.save()

    # Create reminders for project1
    reminder = Reminder(project_id = project1.id,day=3,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "3 days are overdue the deadline. Please send your data for Clinic Test Project.")
    reminder.save()

    # Create reminders for project1
    reminder = Reminder(project_id = project1.id,day=4,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "4 days are overdue the deadline. Please send your data for Clinic Test Project.")
    reminder.save()

    # Create reminders for project1
    reminder = Reminder(project_id = project1.id,day=5,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "5 days are overdue the deadline. Please send your data for Clinic Test Project.")
    reminder.save()

    # Create reminders for project1
    reminder = Reminder(project_id = project1.id,day=6,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "6 days are overdue the deadline. Please send your data for Clinic Test Project.")
    reminder.save()

    # Create reminders for project1
    reminder = Reminder(project_id = project1.id,day=7,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "7 days are overdue the deadline. Please send your data for Clinic Test Project.")
    reminder.save()

    # Associate datasenders/reporters with project 1
    project1.data_senders.extend(["rep5","rep6","rep1"])
    project1.save(manager)

    form_model2 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli002", type='survey',
                            fields=[question1, question2, question3, question4, question5, question6, question7,
                                    question8],
                            entity_type=CLINIC_ENTITY_TYPE)
    try:
        qid2 = form_model2.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli002").delete()
        qid2 = form_model2.save()
    project2 = Project(name="Clinic2 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms"], activity_report='no', sender_group="close",
                       reminder_and_deadline=weekly_reminder_and_deadline)
    project2.qid = qid2
    project2.state = ProjectState.ACTIVE
    try:
        project2.save(manager)
    except Exception:
        pass

    form_model3 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli003", type='survey',
                            fields=[question1, question2, question3, question4, question5, question6, question7],
                            entity_type=CLINIC_ENTITY_TYPE, state=attributes.TEST_STATE)
    try:
        qid3 = form_model3.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli003").delete()
        qid3 = form_model3.save()
    project3 = Project(name="Clinic3 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms"], activity_report='no', sender_group="close",
                       reminder_and_deadline={'frequency_enabled':'False', 'reminders_enabled': 'False'})
    project3.qid = qid3
    project3.state = ProjectState.TEST
    try:
        project3.save(manager)
    except Exception:
        pass

    form_model4 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli004", type='survey',
                            fields=[question1, question2, question3, question4, question5, question6, question7],
                            entity_type=CLINIC_ENTITY_TYPE, state=attributes.TEST_STATE)
    try:
        qid4 = form_model4.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli004").delete()
        qid4 = form_model4.save()
    project4 = Project(name="Clinic4 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms"], activity_report='no', sender_group="close",
                       reminder_and_deadline={'frequency_enabled':'False', 'reminders_enabled': 'False'})
    project4.qid = qid4
    project4.state = ProjectState.TEST
    try:
        project4.save(manager)
    except Exception:
        pass

    form_model5 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli005", type='survey',
                            fields=[question1, question2, question3, question4, question5, question6, question7],
                            entity_type=CLINIC_ENTITY_TYPE, state=attributes.TEST_STATE)
    try:
        qid5 = form_model5.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli005").delete()
        qid5 = form_model5.save()
    project5 = Project(name="Clinic5 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms"], activity_report='no', sender_group="close",
                       reminder_and_deadline={'frequency_enabled':'False', 'reminders_enabled': 'False'})
    project5.qid = qid5
    project5.state = ProjectState.TEST
    try:
        project5.save(manager)
    except Exception:
        pass

    form_model6 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli006", type='survey',
                            fields=[question1, question2, question3, question4, question5, question6, question7],
                            entity_type=CLINIC_ENTITY_TYPE, state=attributes.TEST_STATE)
    try:
        qid6 = form_model6.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli006").delete()
        qid6 = form_model6.save()
    project6 = Project(name="Clinic6 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms"], activity_report='no', sender_group="close",
                       reminder_and_deadline={'frequency_enabled':'False', 'reminders_enabled': 'False'})
    project6.qid = qid6
    project6.state = ProjectState.TEST
    try:
        project6.save(manager)
    except Exception:
        pass

    form_model7 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli007", type='survey',
                            fields=[question1, question2, question3, question4, question5, question6, question7],
                            entity_type=CLINIC_ENTITY_TYPE, state=attributes.TEST_STATE)
    try:
        qid7 = form_model7.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli007").delete()
        qid7 = form_model7.save()
    project7 = Project(name="Clinic7 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms"], activity_report='no', sender_group="close",
                       reminder_and_deadline={'frequency_enabled':'False', 'reminders_enabled': 'False'})
    project7.qid = qid7
    project7.state = ProjectState.TEST
    try:
        project7.save(manager)
    except Exception:
        pass

    form_model8 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli008", type='survey',
                            fields=[question1, question2, question3, question4, question5, question6, question7],
                            entity_type=CLINIC_ENTITY_TYPE, state=attributes.INACTIVE_STATE)
    try:
        qid8 = form_model8.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli008").delete()
        qid8 = form_model8.save()
    project8 = Project(name="Clinic8 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms"], activity_report='no', sender_group="close",
                       reminder_and_deadline={'frequency_enabled':'False', 'reminders_enabled': 'False'})
    project8.qid = qid8
    project8.state = ProjectState.INACTIVE
    try:
        project8.save(manager)
    except Exception:
        pass

    # Creating a project to test reminders with following deadline.
    weekly_reminder_and_following_deadline = {
            "reminders_enabled": "True",
            "deadline_week": "6",
            "deadline_type": "Following",
            "frequency_enabled": "True",
            "has_deadline": "True",
            "frequency_period": "week"
        }

    form_model10 = FormModel(manager, name="AIDS Clinici", label="Aids form_model",
                            form_code="cli009", type='survey',
                            fields=[question1, question2, question3, question4, question5, question6, question7,
                                    question8],
                            entity_type=CLINIC_ENTITY_TYPE)
    try:
        qid = form_model10.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli009").delete()
        qid = form_model10.save()
    project9 = Project(name="Clinic9 Reminder Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms"], activity_report='no', sender_group="close",
                       reminder_and_deadline=weekly_reminder_and_following_deadline)
    project9.qid = qid
    project9.state = ProjectState.ACTIVE
    try:
        project9.save(manager)
    except Exception:
        pass

    # Create reminders for project2 and project 9
    reminder = Reminder(project_id = project9.id,day=0,reminder_mode=ReminderMode.ON_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "Reminder test")
    reminder.save()

    # Associate datasenders/reporters with project 9
    project9.data_senders.extend(["rep3","rep4"])
    project9.save(manager)

    # Add a submission for reporter 3, for activity period, 2011,9,12 - 2011,9,18
    submission= Submission(manager, TransportInfo('sms', '1234567891', '123'), form_code="cli009",values='reporter 3 submission')
    submission._doc.event_time = datetime(2011,9,16)
    submission.save()

    form_model10 = FormModel(manager, name="AIDS", label="Aids form_model",
                           form_code="cli010", type='survey',
                           fields=[question1, question2, question3, question4, question5, question6, question7, question8],
                           entity_type=CLINIC_ENTITY_TYPE
    )

    weekly_reminder_and_deadline = {
            "reminders_enabled": "True",
            "deadline_week": "5",
            "deadline_type": "Following",
            "frequency_enabled": "True",
            "has_deadline": "True",
            "frequency_period": "week"
        }

    try:
        qid10 = form_model10.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli010").delete()
        qid10 = form_model10.save()
    project10 = Project(name="Clinic DS W/O Submission (Following)", goals="This project is for automation", project_type="survey",
                      entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms"], activity_report='no', sender_group="close",
                      reminder_and_deadline=weekly_reminder_and_deadline)
    project10.qid = qid10
    project10.state = ProjectState.ACTIVE
    try:
        project10.save(manager)
    except Exception:
        pass

    # Create reminders for project10
    reminder = Reminder(project_id = project10.id,day=1,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "1 day is remainning to deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()

    # Create reminders for project10
    reminder = Reminder(project_id = project10.id,day=2,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "2 days are remainning to deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()

    # Create reminders for project10
    reminder = Reminder(project_id = project10.id,day=3,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "3 days are remainning to deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()

    # Create reminders for project10
    reminder = Reminder(project_id = project10.id,day=4,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "4 days are remainning to deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()

    # Create reminders for project10
    reminder = Reminder(project_id = project10.id,day=5,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "5 days are remainning to deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()

    # Create reminders for project10
    reminder = Reminder(project_id = project10.id,day=0,reminder_mode=ReminderMode.ON_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "Today is the deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()

    # Create reminders for project10
    reminder = Reminder(project_id = project10.id,day=1,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "1 day is overdue the deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()

    # Create reminders for project10
    reminder = Reminder(project_id = project10.id,day=2,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "2 days are overdue the deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()

    # Create reminders for project10
    reminder = Reminder(project_id = project10.id,day=3,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "3 days are overdue the deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()

    # Create reminders for project10
    reminder = Reminder(project_id = project10.id,day=4,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "4 days are overdue the deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()

    # Create reminders for project10
    reminder = Reminder(project_id = project10.id,day=5,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "5 days are overdue the deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()

    # Create reminders for project10
    reminder = Reminder(project_id = project10.id,day=6,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "6 days are overdue the deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()

    # Create reminders for project10
    reminder = Reminder(project_id = project10.id,day=7,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "7 days are overdue the deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()

    # Associate datasenders/reporters with project 1
    project10.data_senders.extend(["rep5","rep6","rep7"])
    project10.save(manager)

    form_model11 = FormModel(manager, name="AIDS", label="Aids form_model",
                           form_code="cli011", type='survey',
                           fields=[question1, question2, question3, question4, question5, question6, question7, question8],
                           entity_type=CLINIC_ENTITY_TYPE
    )

    weekly_reminder_and_deadline = {
            "reminders_enabled": "True",
            "deadline_week": "5",
            "deadline_type": "Following",
            "frequency_enabled": "True",
            "has_deadline": "True",
            "frequency_period": "week"
        }

    try:
        qid11 = form_model11.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli011").delete()
        qid11 = form_model11.save()
    project11 = Project(name="Clinic All DS (Following)", goals="This project is for automation", project_type="survey",
                      entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms"], activity_report='no', sender_group="close",
                      reminder_and_deadline=weekly_reminder_and_deadline)
    project11.qid = qid11
    project11.state = ProjectState.ACTIVE
    try:
        project11.save(manager)
    except Exception:
        pass

    # Create reminders for project11
    reminder = Reminder(project_id = project11.id,day=1,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "1 day is remainning to deadline. Please send your data for Clinic11 Test Project.")
    reminder.save()

    # Create reminders for project11
    reminder = Reminder(project_id = project11.id,day=2,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "2 days are remainning to deadline. Please send your data for Clinic11 Test Project.")
    reminder.save()

    # Create reminders for project11
    reminder = Reminder(project_id = project11.id,day=3,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "3 days are remainning to deadline. Please send your data for Clinic11 Test Project.")
    reminder.save()

    # Create reminders for project11
    reminder = Reminder(project_id = project11.id,day=4,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "4 days are remainning to deadline. Please send your data for Clinic11 Test Project.")
    reminder.save()

    # Create reminders for project11
    reminder = Reminder(project_id = project11.id,day=5,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "5 days are remainning to deadline. Please send your data for Clinic11 Test Project.")
    reminder.save()

    # Create reminders for project11
    reminder = Reminder(project_id = project11.id,day=0,reminder_mode=ReminderMode.ON_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "Today is the deadline. Please send your data for Clinic11 Test Project.")
    reminder.save()

    # Create reminders for project11
    reminder = Reminder(project_id = project11.id,day=1,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "1 day is overdue the deadline. Please send your data for Clinic11 Test Project.")
    reminder.save()

    # Create reminders for project11
    reminder = Reminder(project_id = project11.id,day=2,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "2 days are overdue the deadline. Please send your data for Clinic11 Test Project.")
    reminder.save()

    # Create reminders for project11
    reminder = Reminder(project_id = project11.id,day=3,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "3 days are overdue the deadline. Please send your data for Clinic11 Test Project.")
    reminder.save()

    # Create reminders for project11
    reminder = Reminder(project_id = project11.id,day=4,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "4 days are overdue the deadline. Please send your data for Clinic11 Test Project.")
    reminder.save()

    # Create reminders for project11
    reminder = Reminder(project_id = project11.id,day=5,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "5 days are overdue the deadline. Please send your data for Clinic11 Test Project.")
    reminder.save()

    # Create reminders for project11
    reminder = Reminder(project_id = project11.id,day=6,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "6 days are overdue the deadline. Please send your data for Clinic11 Test Project.")
    reminder.save()

    # Create reminders for project11
    reminder = Reminder(project_id = project11.id,day=7,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.ALL_DATASENDERS,organization_id = 'SLX364903',
             message = "7 days are overdue the deadline. Please send your data for Clinic11 Test Project.")
    reminder.save()

    # Associate datasenders/reporters with project 1
    project11.data_senders.extend(["rep5","rep6","rep7"])
    project11.save(manager)

    form_model12 = FormModel(manager, name="AIDS", label="Aids form_model",
                           form_code="cli012", type='survey',
                           fields=[question1, question2, question3, question4, question5, question6, question7, question8],
                           entity_type=CLINIC_ENTITY_TYPE
    )

    weekly_reminder_and_deadline = {
            "reminders_enabled": "True",
            "deadline_week": "5",
            "deadline_type": "That",
            "frequency_enabled": "True",
            "has_deadline": "True",
            "frequency_period": "week"
        }

    try:
        qid12 = form_model12.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli012").delete()
        qid12 = form_model12.save()
    project12 = Project(name="Clinic DS W/O Submission (That)", goals="This project is for automation", project_type="survey",
                      entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web"], activity_report='no', sender_group="close",
                      reminder_and_deadline=weekly_reminder_and_deadline)
    project12.qid = qid12
    project12.state = ProjectState.ACTIVE

    try:
        project12.save(manager)
    except Exception:
        pass

    # Create reminders for project12
    reminder = Reminder(project_id = project12.id,day=1,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "1 day is remainning to deadline. Please send your data for Clinic12 Test Project.")
    reminder.save()

    # Create reminders for project12
    reminder = Reminder(project_id = project12.id,day=2,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "2 days are remainning to deadline. Please send your data for Clinic12 Test Project.")
    reminder.save()

    # Create reminders for project12
    reminder = Reminder(project_id = project12.id,day=3,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "3 days are remainning to deadline. Please send your data for Clinic12 Test Project.")
    reminder.save()

    # Create reminders for project12
    reminder = Reminder(project_id = project12.id,day=4,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "4 days are remainning to deadline. Please send your data for Clinic12 Test Project.")
    reminder.save()

    # Create reminders for project12
    reminder = Reminder(project_id = project12.id,day=5,reminder_mode=ReminderMode.BEFORE_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "5 days are remainning to deadline. Please send your data for Clinic12 Test Project.")
    reminder.save()

    # Create reminders for project12
    reminder = Reminder(project_id = project12.id,day=0,reminder_mode=ReminderMode.ON_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "Today is the deadline. Please send your data for Clinic12 Test Project.")
    reminder.save()

    # Create reminders for project12
    reminder = Reminder(project_id = project12.id,day=1,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "1 day is overdue the deadline. Please send your data for Clinic12 Test Project.")
    reminder.save()

    # Create reminders for project12
    reminder = Reminder(project_id = project12.id,day=2,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "2 days are overdue the deadline. Please send your data for Clinic12 Test Project.")
    reminder.save()

    # Create reminders for project12
    reminder = Reminder(project_id = project12.id,day=3,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "3 days are overdue the deadline. Please send your data for Clinic12 Test Project.")
    reminder.save()

    # Create reminders for project12
    reminder = Reminder(project_id = project12.id,day=4,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "4 days are overdue the deadline. Please send your data for Clinic12 Test Project.")
    reminder.save()

    # Create reminders for project12
    reminder = Reminder(project_id = project12.id,day=5,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "5 days are overdue the deadline. Please send your data for Clinic12 Test Project.")
    reminder.save()

    # Create reminders for project12
    reminder = Reminder(project_id = project12.id,day=6,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "6 days are overdue the deadline. Please send your data for Clinic12 Test Project.")
    reminder.save()

    # Create reminders for project12
    reminder = Reminder(project_id = project12.id,day=7,reminder_mode=ReminderMode.AFTER_DEADLINE,
             remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS,organization_id = 'SLX364903',
             message = "7 days are overdue the deadline. Please send your data for Clinic12 Test Project.")
    reminder.save()

    # Associate datasenders/reporters with project 1
    project12.data_senders.extend(["rep5","rep6","rep7"])
    project12.save(manager)


def load_sms_data_for_cli001(manager):
    FEB = datetime(2011, 02, 28, hour=12, minute=00, second=00, tzinfo=UTC)
    MARCH = datetime(2011, 03, 01, tzinfo=UTC)
    DEC_2010 = datetime(2010, 12, 28, hour=00, minute=00, second=59, tzinfo=UTC)
    NOV_2010 = datetime(2010, 11, 26, hour=23, minute=59, second=59, tzinfo=UTC)
    today = datetime.today()
    LAST_WEEK = today - timedelta(days=7)
    THIS_MONTH = datetime(today.year, today.month, 1, 12, 45, 58)
    PREV_MONTH = THIS_MONTH - timedelta(days=8)
    sms_player = SMSPlayer(manager, get_location_tree())
    FROM_NUMBER = '1234567890'
    TO_NUMBER = '919880734937'
    transport = TransportInfo(SMS, FROM_NUMBER, TO_NUMBER)

    message1 = "reg .t  clinic .n  Clinic in Analalava  .l  Analalava  .g  -14.6333  47.7667  .d This is a Clinic in Analalava .m 987654321"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "reg .t  clinic .n  Clinic in Andapa  .l  Andapa  .g  -14.65  49.6167  .d This is a Clinic in Andapa  .m 87654322"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "reg .t  clinic .n  Clinic in Antalaha  .l  Antalaha  .g  -14.8833  50.25  .d This is a Clinic in Antalaha  .m 87654323"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "reg .t  clinic .n  Clinic in ANALAMANGA  .l  ANALAMANGA  .g  -18.8  47.4833  .d This is a Clinic in Antananarivo  .m 87654324"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "reg .t  clinic .n  Clinic in TSIMANARIRAZANA .l  TSIMANARIRAZANA .g  -12.35  49.3  .d This is a Clinic in Diégo–Suarez .m 87654325"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "reg .t  clinic .n  Clinic in Antsirabe  .l  Antsirabe  .g  -19.8167  47.0667  .d This is a Clinic in Antsirabe  .m 87654326"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "reg .t  clinic .n  Clinic in Besalampy  .l  Besalampy  .g  -16.75  44.5  .d This is a Clinic in Besalampy  .m 87654327"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "reg .t  clinic .n  clinique à Farafangana  .l  Farafangana  .g  -22.8  47.8333  .d This is a Clinic in Farafangana  .m 87654328"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "reg .t  clinic .n  Clinic in Fianarantsoa I .l  Fianarantsoa I .g  -21.45  47.1 .d  C'est une clinique à Fianarantsoa .m 87654329"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "reg .t  clinic .n  Clinic in Sainte Marie  .l  Sainte Marie  .g  -17.0833  49.8167  .d This is a Clinic in Île Sainte–Marie  .m 87654330"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "reg .t  clinic .n  Clinic in Mahajanga .l  Mahajanga .g  -15.6667  46.35  .d This is a Clinic in Mahajanga .m 87654331"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    datetime_mocker = DateTimeMocker()
    datetime_mocker.set_date_time_now(FEB)
    # Total number of identical records = 3
    message1 = "cli001 .EID cid001 .NA Mr. Tessy .FA 58 .RD 28.02.2011 .BG c .SY ade .GPS 79.2 20.34567"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cid002 .NA Mr. Adam .FA 62 .RD 15.02.2011 .BG a .SY ab .GPS 74.2678 23.3567"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cid003 .NA Ms. Beth .FA 75 .RD 09.02.2011 .BG b .SY bc .GPS 18.245 29.3123"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    datetime_mocker.set_date_time_now(MARCH)
    # Total number of identical records = 4
    message1 = "cli001 .EID cid004 .NA Jannita .FA 90 .RD 07.03.2011 .BG b .SY bbe .GPS 45.233 28.3324"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cid005 .NA Aanda .FA 58 .RD 12.03.2011 .BG c .SY bd .GPS 40.2 69.3123"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = 'cli001 .EID cid001 .NA Ianda (",) .FA 34 .RD 27.03.2011 .BG d .SY be .GPS 38.3452 15.3345'
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cid001 .NA ànita .FA 45 .RD 07.03.2011 .BG b .SY bbe .GPS 45.233 28.3324"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cid004 .NA Amanda .FA 81 .RD 12.03.2011 .BG c .SY bd .GPS 40.2 69.3123"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = 'cli001 .EID cid005 .NA Vanda (",) .FA 34 .RD 27.03.2011 .BG d .SY be .GPS 38.3452 15.3345'
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cid003 .NA ànnita .FA 80 .RD 07.03.2011 .BG b .SY bbe .GPS 45.233 28.3324"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cid002 .NA Amanda .FA 69 .RD 12.03.2011 .BG c .SY bd .GPS 40.2 69.3123"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = 'cli001 .EID cid004 .NA Panda (",) .FA 34 .RD 27.03.2011 .BG d .SY be .GPS 38.3452 15.3345'
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cid005 .NA ànnita .FA 50 .RD 07.03.2011 .BG b .SY bbe .GPS 45.233 28.3324"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cid003 .NA Jimanda .FA 86 .RD 12.03.2011 .BG c .SY bd .GPS 40.2 69.3123"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = 'cli001 .EID cli10 .NA Kanda (",) .FA 64 .RD 27.03.2011 .BG d .SY be .GPS 38.3452 15.3345'
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cid004 .NA ànnita .FA 30 .RD 07.03.2011 .BG b .SY bbe .GPS 45.233 28.3324"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cid005 .NA Qamanda  .FA 47 .RD 12.03.2011 .BG c .SY bd .GPS 40.2 69.3123"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = 'cli001 .EID cid001 .NA Huanda (*_*) .FA 74 .RD 27.03.2011 .BG d .SY be .GPS 38.3452 15.3345'
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    datetime_mocker.set_date_time_now(DEC_2010)
    # Total number of identical records = 4
    message1 = "cli001 .EID cli12 .NA Jugal .FA 47 .RD 15.12.2010 .BG d .SY ace .GPS -58.3452 19.3345"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli11 .NA De'melo .FA 38 .RD 27.12.2010 .BG c .SY ba .GPS 81.672 92.33456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli13 .NA Dono`mova .FA 24 .RD 06.12.2010 .BG b .SY cd .GPS 65.23452 -28.3456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli15 .NA Aàntra .FA 89 .RD 11.12.2010 .BG a .SY bd .GPS 45.234 89.32345"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    datetime_mocker.set_date_time_now(NOV_2010)
    # Total number of identical records = 3
    message1 = "cli001 .EID cli12 .NA ànnita .FA 90 .RD 07.11.2010 .BG b .SY bbe .GPS 45.233 28.3324"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli14 .NA Amanda .FA 67 .RD 12.11.2010 .BG c .SY bd .GPS 40.2 69.3123"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = 'cli001 .EID cli8 .NA Kanda (",) .FA 34 .RD 27.11.2010 .BG d .SY be .GPS 38.3452 15.3345'
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli9 .NA ànnita .FA 90 .RD 17.11.2010 .BG b .SY bbe .GPS 45.233 28.3324"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cid007 .NA Amanda .FA 73 .RD 12.11.2010 .BG c .SY bd .GPS 40.2 69.3123"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = 'cli001 .EID cli8 .NA Kanda (",) .FA 34 .RD 27.11.2010 .BG d .SY be .GPS 38.3452 15.3345'
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    datetime_mocker.set_date_time_now(PREV_MONTH)
    month = today.month - 1
    year = today.year
    if not(month):
        month = 12
        year = today.year - 1
    Last_month_date = "12." + str(month) + "." + str(year)
    # Total number of identical records = 4
    message1 = "cli001 .EID cli9 .NA Demelo .FA 38 .RD " + Last_month_date + " .BG c .SY ba .GPS 19.672 92.33456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli10 .NA Zorro .FA 48 .RD " + Last_month_date + " .BG b .SY cd .GPS 23.23452 -28.3456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli11 .NA Aàntra .FA 98 .RD " + Last_month_date + " .BG a .SY cb .GPS -45.234 89.32345"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli12 .NA ànnita .FA 37 .RD " + Last_month_date + " .BG d .SY cbe .GPS -78.233 -28.3324"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli9 .NA Demelo .FA 38 .RD " + Last_month_date + " .BG c .SY ba .GPS 19.672 92.33456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli10 .NA Zorro .FA 48 .RD " + Last_month_date + " .BG b .SY cd .GPS 23.23452 -28.3456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli11 .NA Aàntra .FA 95 .RD " + Last_month_date + " .BG a .SY cb .GPS -45.234 89.32345"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli12 .NA ànnita .FA 35 .RD " + Last_month_date + " .BG d .SY cbe .GPS -78.233 -28.3324"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli9 .NA Demelo .FA 32 .RD " + Last_month_date + " .BG c .SY ba .GPS 19.672 92.33456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli10 .NA Zorro .FA 43 .RD " + Last_month_date + " .BG b .SY cd .GPS 23.23452 -28.3456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli11 .NA Aàntra .FA 91 .RD " + Last_month_date + " .BG a .SY be .GPS -45.234 89.32345"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli12 .NA ànnita .FA 45 .RD " + Last_month_date + " .BG d .SY cbe .GPS -78.233 -28.3324"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    datetime_mocker.set_date_time_now(THIS_MONTH)
    current_month_date = "01." + str(today.month) + "." + str(today.year)
    # Total number of identical records = 4
    message1 = "cli001 .EID cli13 .NA Dmanda .FA 69 .RD " + current_month_date + " .BG c .SY ce .GPS 40.2 69.3123"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli14 .NA Vamand .FA 36 .RD " + current_month_date + " .BG a .SY ace .GPS 58.3452 115.3345"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli15 .NA M!lo .FA 88 .RD " + current_month_date + " .BG b .SY ba .GPS 19.672 92.33456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli16 .NA K!llo .FA 88 .RD " + current_month_date + " .BG a .SY ac .GPS 19.672 92.33456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli13 .NA Dmanda .FA 89 .RD " + current_month_date + " .BG c .SY ce .GPS 40.2 69.3123"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli14 .NA Vamand .FA 56 .RD " + current_month_date + " .BG a .SY ace .GPS 58.3452 115.3345"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli15 .NA M!lo .FA 45 .RD " + current_month_date + " .BG c .SY ca .GPS 19.672 92.33456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli16 .NA K!llo .FA 28 .RD " + current_month_date + " .BG b .SY ae .GPS 19.672 92.33456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    datetime_mocker.end_mock()

    today_date = str(today.day) + "." + str(today.month) + "." + str(today.year)
    # Total number of identical records = 3
    message1 = "cli001 .EID cli17 .NA Catty .FA 78 .RD " + today_date + " .BG b .SY dce .GPS 33.23452 -68.3456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli18 .NA àntra .FA 28 .RD " + today_date + " .BG a .SY adb .GPS -45.234 169.32345"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli9 .NA Tinnita .RD " + today_date + " .FA 37 .BG d .SY ace .GPS -78.233 -28.3324"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    message1 = "cli001 .EID cli17 .NA Catty .FA 98 .RD " + today_date + " .BG b .SY dce .GPS 33.23452 -68.3456"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli001 .EID cli18 .NA àntra .FA 58 .RD " + today_date + " .BG a .SY adb .GPS -45.234 169.32345"
    response = sms_player.accept(Request(transportInfo=
                                         transport, message=message1))
    message1 = "cli001 .EID cli9 .NA Tinnita .RD " + today_date + " .FA 27 .BG d .SY ace .GPS -78.233 -28.3324"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    FROM_NUMBER = '919970059125'
    TO_NUMBER = '919880734937'
    transport = TransportInfo(SMS, FROM_NUMBER, TO_NUMBER)

    datetime_mocker2 = DateTimeMocker()
    datetime_mocker2.set_date_time_now(LAST_WEEK)
    last_week_date = str(LAST_WEEK.day) + "." + str(LAST_WEEK.month) + "." + str(LAST_WEEK.year)
    # Total number of identical records = 4
    message1 = "cli010 .EID cli13 .NA Dmanda .FA 69 .RD " + last_week_date + " .BG c .SY ce .GPS 40.2 69.3123 .RM a"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli010 .EID cli14 .NA Vamand .FA 36 .RD " + last_week_date + " .BG a .SY ace .GPS 58.3452 115.3345 .RM b"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli010 .EID cli15 .NA M!lo .FA 88 .RD " + last_week_date + " .BG b .SY ba .GPS 19.672 92.33456 .RM c"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    # Total number of identical records = 4
    message1 = "cli012 .EID cli13 .NA Dmanda .FA 69 .RD " + last_week_date + " .BG c .SY ce .GPS 40.2 69.3123 .RM a"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli012 .EID cli14 .NA Vamand .FA 36 .RD " + last_week_date + " .BG a .SY ace .GPS 58.3452 115.3345 .RM b"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli012 .EID cli15 .NA M!lo .FA 88 .RD " + last_week_date + " .BG b .SY ba .GPS 19.672 92.33456 .RM c"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    # Total number of identical records = 4
    message1 = "cli011 .EID cli13 .NA Dmanda .FA 69 .RD " + last_week_date + " .BG c .SY ce .GPS 40.2 69.3123 .RM a"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli011 .EID cli14 .NA Vamand .FA 36 .RD " + last_week_date + " .BG a .SY ace .GPS 58.3452 115.3345 .RM b"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli011 .EID cli15 .NA M!lo .FA 88 .RD " + last_week_date + " .BG b .SY ba .GPS 19.672 92.33456 .RM c"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    datetime_mocker2.end_mock()

    FROM_NUMBER = '917798987102'
    TO_NUMBER = '919880734937'
    transport = TransportInfo(SMS, FROM_NUMBER, TO_NUMBER)

    today_date = str(today.day) + "." + str(today.month) + "." + str(today.year)
    # Total number of identical records = 3
    message1 = "cli010 .EID cli16 .NA Catty .FA 78 .RD " + today_date + " .BG b .SY dce .GPS 33.23452 -68.3456 .RM a"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli010 .EID cli17 .NA àntra .FA 28 .RD " + today_date + " .BG a .SY adb .GPS -45.234 169.32345 .RM c"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli010 .EID cli18 .NA Tinnita .RD " + today_date + " .FA 37 .BG d .SY ace .GPS -78.233 -28.3324 .RM d"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    # Total number of identical records = 3
    message1 = "cli011 .EID cli16 .NA Catty .FA 78 .RD " + today_date + " .BG b .SY dce .GPS 33.23452 -68.3456 .RM a"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli011 .EID cli17 .NA àntra .FA 28 .RD " + today_date + " .BG a .SY adb .GPS -45.234 169.32345 .RM c"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli011 .EID cli18 .NA Tinnita .RD " + today_date + " .FA 37 .BG d .SY ace .GPS -78.233 -28.3324 .RM d"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

    # Total number of identical records = 3
    message1 = "cli012 .EID cli16 .NA Catty .FA 78 .RD " + today_date + " .BG b .SY dce .GPS 33.23452 -68.3456 .RM a"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli012 .EID cli17 .NA àntra .FA 28 .RD " + today_date + " .BG a .SY adb .GPS -45.234 169.32345 .RM c"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))
    message1 = "cli012 .EID cli18 .NA Tinnita .RD " + today_date + " .FA 37 .BG d .SY ace .GPS -78.233 -28.3324 .RM d"
    response = sms_player.accept(Request(transportInfo=transport, message=message1))

def create_clinic_project_for_trial_account(CLINIC_ENTITY_TYPE, manager, trial_org_pk):
    organization = Organization.objects.get(pk=trial_org_pk)
    Reminder.objects.filter(organization = organization).delete()
    name_type = create_data_dict(manager, name='Name', slug='Name', primitive_type='string')
    # Entity id is a default type in the system.
    entity_id_type = get_datadict_type_by_slug(manager, slug='entity_id')
    age_type = create_data_dict(manager, name='Age Type', slug='age', primitive_type='integer')
    date_type = create_data_dict(manager, name='Report Date', slug='date', primitive_type='date')
    select_type = create_data_dict(manager, name='Choice Type', slug='choice', primitive_type='select')
    geo_code_type = create_data_dict(manager, name='GeoCode Type', slug='geo_code', primitive_type='geocode')
    question1 = TextField(label="entity_question", code="EID", name="What is associatéd entity?",
                          language="en", entity_question_flag=True, ddtype=entity_id_type,
                          constraints=[TextLengthConstraint(min=1, max=12)],
                          instruction="Answer must be a word or phrase 12 characters maximum")
    question2 = TextField(label="Name", code="NA", name="What is your namé?",
                          constraints=[TextLengthConstraint(min=1, max=10)],
                          defaultValue="some default value", language="en", ddtype=name_type,
                          instruction="Answer must be a word or phrase 10 characters maximum")
    question3 = IntegerField(label="Father age", code="FA", name="What is age öf father?",
                             constraints=[NumericRangeConstraint(min=18, max=100)], ddtype=age_type,
                             instruction="Answer must be a number between 18-100.")
    question4 = DateField(label="Report date", code="RD", name="What is réporting date?",
                          date_format="dd.mm.yyyy", ddtype=date_type,
                          instruction="Answer must be a date in the following format: day.month.year. Example: 25.12.2011")
    question5 = SelectField(label="Blood Group", code="BG", name="What is your blood group?",
                            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True,
                            ddtype=select_type, instruction="Choose 1 answer from the list.")
    question6 = SelectField(label="Symptoms", code="SY", name="What aré symptoms?",
                            options=[("Rapid weight loss", "a"), ("Dry cough", "b"), ("Pneumonia", "c"),
                                    ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False,
                            ddtype=select_type,
                            instruction="Choose 1 or more answers from the list.")
    question7 = GeoCodeField(name="What is the GPS codé for clinic", code="GPS",
                             label="What is the GPS code for clinic?",
                             language="en", ddtype=geo_code_type,
                             instruction="Answer must be GPS co-ordinates in the following format: xx.xxxx yy.yyyy Example: -18.1324 27.6547")
    question8 = SelectField(label="Required Medicines", code="RM", name="What are the required medicines?",
                            options=[("Hivid", "a"), ("Rétrovir", "b"), ("Vidéx EC", "c"), ("Epzicom", "d")],
                            single_select_flag=False,
                            ddtype=select_type,
                            instruction="Choose 1 or more answers from the list.", required=False)
    form_model = FormModel(manager, name="AIDS", label="Aids form_model",
                           form_code="cli001", type='survey',
                           fields=[question1, question2, question3, question4, question5, question6, question7,
                                   question8],
                           entity_type=CLINIC_ENTITY_TYPE
    )

    weekly_reminder_and_deadline = {
            "reminders_enabled": "True",
            "deadline_week": "5",
            "deadline_type": "That",
            "frequency_enabled": "True",
            "has_deadline": "True",
            "frequency_period": "week"
        }

    try:
        qid = form_model.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli001").delete()
        qid = form_model.save()
    project1 = Project(name="Clinic Test Project", goals="This project is for automation", project_type="survey",
                      entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web"], activity_report='no', sender_group="close",
                      reminder_and_deadline=weekly_reminder_and_deadline)
    project1.qid = qid
    project1.state = ProjectState.ACTIVE
    try:
        project1.save(manager)
    except Exception:
        pass

def load_data():
    manager = load_manager_for_default_test_account()
    initializer.run(manager)
    CLINIC_ENTITY_TYPE = [u"clinic"]
    WATER_POINT_ENTITY_TYPE = [u"waterpoint"]
    create_entity_types(manager, [CLINIC_ENTITY_TYPE, WATER_POINT_ENTITY_TYPE])
    load_datadict_types(manager)
    load_clinic_entities(CLINIC_ENTITY_TYPE, manager)
    load_waterpoint_entities(WATER_POINT_ENTITY_TYPE, manager)
    create_clinic_projects(CLINIC_ENTITY_TYPE, manager)
    #Register Reporters
    phone_number_type = create_data_dict(manager, name='Telephone Number', slug='telephone_number',
                                         primitive_type='string')
    first_name_type = create_data_dict(manager, name='First Name', slug='first_name', primitive_type='string')
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "1234567890", phone_number_type),
            (NAME_FIELD, "Shweta", first_name_type)],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep1", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "261332592634", phone_number_type),
            (NAME_FIELD, "David", first_name_type)],
             location=[u'Madagascar', u'Haute matsiatra', u'Ambohimahasoa', u'Camp Robin'],
             short_code="rep2", geometry={"type": "Point", "coordinates": [-20.9027586764, 47.165034158]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "1234567891", phone_number_type),
            (NAME_FIELD, "Shilpa", first_name_type)],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep3", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "1234567892", phone_number_type),
        (NAME_FIELD, "Asif", first_name_type)],
         location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
         short_code="rep4", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "919970059125", phone_number_type),
        (NAME_FIELD, "Ritesh", first_name_type)],
         location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
         short_code="rep5", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "917798987116", phone_number_type),
        (NAME_FIELD, "RiteshY", first_name_type)],
         location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
         short_code="rep6", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "917798987102", phone_number_type),
        (NAME_FIELD, "AkshaY", first_name_type)],
         location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
         short_code="rep7", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})

    load_sms_data_for_cli001(manager)

    create_trial_test_organization('chinatwu@gmail.com','COJ00000')
    create_trial_test_organization('chinatwu2@gmail.com','COJ00001')
    create_trial_test_organization('chinatwu3@gmail.com','COJ00002')
    create_trial_test_organization('chinatwu4@gmail.com','COJ00003')

def create_trial_test_organization(email, org_id):
    manager = get_database_manager(User.objects.get(username=email))
    initializer.run(manager)
    CLINIC_ENTITY_TYPE = [u"clinic"]
    WATER_POINT_ENTITY_TYPE = [u"waterpoint"]
    create_entity_types(manager, [CLINIC_ENTITY_TYPE, WATER_POINT_ENTITY_TYPE])
    load_datadict_types(manager)
    load_clinic_entities(CLINIC_ENTITY_TYPE, manager)
    load_waterpoint_entities(WATER_POINT_ENTITY_TYPE, manager)
    create_clinic_project_for_trial_account(CLINIC_ENTITY_TYPE, manager, org_id)

def load_test_managers():
    test_emails = ['tester150411@gmail.com', 'chinatwu@gmail.com', 'chinatwu2@gmail.com', 'chinatwu3@gmail.com', 'chinatwu4@gmail.com']
    return [get_database_manager(User.objects.get(username=email)) for email in test_emails]

def load_all_managers():
    managers = []
    for org in OrganizationSetting.objects.all():
        db = org.document_store
        manager = get_db_manager(server=settings.COUCH_DB_SERVER, database=db)
        managers.append(manager)
    return managers

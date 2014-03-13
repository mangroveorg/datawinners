# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from mock import patch
from pytz import UTC

from datawinners import initializer
from datawinners.accountmanagement.models import OrganizationSetting, Organization, TEST_REPORTER_MOBILE_NUMBER
from datawinners.location.LocationTree import get_location_hierarchy, get_location_tree
from datawinners.main.management.commands.utils import TEST_EMAILS
from datawinners.project.models import Project, Reminder, ReminderMode
from datawinners.messageprovider.messages import SMS
from datawinners.feeds.database import get_feeds_database
from datawinners.main.database import get_database_manager, get_db_manager
from datawinners.main.initial_template_creation import create_questionnaire_templates
from mangrove.errors.MangroveException import DataObjectAlreadyExists
from mangrove.form_model.field import TextField, IntegerField, DateField, SelectField, GeoCodeField, UniqueIdField
from mangrove.form_model.form_model import FormModel, NAME_FIELD, MOBILE_NUMBER_FIELD, get_form_model_by_code
from mangrove.form_model.validation import NumericRangeConstraint, TextLengthConstraint
from mangrove.transport.player.player import SMSPlayer
from mangrove.transport import Request, TransportInfo
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE
from datawinners.tests.test_data_utils import load_manager_for_default_test_account, create_entity_types, define_entity_instance, register
from mangrove.transport.player.new_players import SMSPlayerV2, WebPlayerV2
from datawinners.submission.location import LocationBridge


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


def load_clinic_entities(CLINIC_ENTITY_TYPE, manager):
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MP', 'Bhopal'], short_code="cid001",
                               geometry={"type": "Point", "coordinates": [23.2833, 77.35]},
                               name="Test", firstname="Bhopal Clinic", description="This a clinic in Bhopal.",
                               mobile_number="123456")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Surgeon"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MP', 'Satna'], short_code="cid002",
                               geometry={"type": "Point", "coordinates": [24.5667, 80.8333]},
                               name="Test", firstname="Satna Clinic", description="This a clinic in Satna.",
                               mobile_number="123457")
    e.set_aggregation_path("governance", ["Director", "Med_Supervisor", "Surgeon"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MP', 'Jabalpur'], short_code="cid003",
                               geometry={"type": "Point", "coordinates": [23.2, 79.95]},
                               name="Test", firstname="Jabalpur Clinic", description="This a clinic in Jabalpur.",
                               mobile_number="123458")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Doctor"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'MP', 'Khandwa'], short_code="cid004",
                               geometry={"type": "Point", "coordinates": [21.8333, 76.3667]},
                               name="Test", firstname="Khandwa Clinic", description="This a clinic in Khandwa.",
                               mobile_number="123459")
    e.set_aggregation_path("governance", ["Director", "Med_Supervisor", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Kerala', 'Kochi'], short_code="cid005",
                               geometry={"type": "Point", "coordinates": [9.939248, 76.259625]},
                               name="Test", firstname="Kochi Clinic", description="This a clinic in Kochi.",
                               mobile_number="123460")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Madhya Pradesh', 'New Gwalior'],
                               short_code="cid006", geometry={"type": "Point", "coordinates": [26.227112, 78.18708]},
                               name="Test", firstname="New Gwalior Clinic", description="This a clinic in New Gwalior.",
                               mobile_number="1234561")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, CLINIC_ENTITY_TYPE, ['India', 'Madhya Pradesh', 'Indore'], short_code="cid007",
                               geometry={"type": "Point", "coordinates": [22.7167, 75.8]},
                               name="Test", firstname="Indore Clinic", description="This a clinic in Indore.",
                               mobile_number="1234562")
    e.set_aggregation_path("governance", ["Director", "Med_Officer", "Nurse"])
    try:
        e.save()
    except Exception:
        pass


def load_waterpoint_entities(WATER_POINT_ENTITY_TYPE, manager):
    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Gujrat', 'Ahmedabad'], short_code="wp01",
                               geometry={"type": "Point", "coordinates": [23.0395677, 72.566005]},
                               name="Test", firstname="Ahmedabad waterpoint",
                               description="This a waterpoint in Ahmedabad.",
                               mobile_number="1234563")
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Gujrat', 'Bhuj'], short_code="wp02",
                               geometry={"type": "Point", "coordinates": [23.251671, 69.66256]},
                               name="Test", firstname="Bhuj waterpoint", description="This a waterpoint in Bhuj.",
                               mobile_number="1234564")
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass
    e = define_entity_instance(manager, WATER_POINT_ENTITY_TYPE, ['India', 'Haryana', 'Gurgaon'], short_code="wp03",
                               geometry={"type": "Point", "coordinates": [28.46385, 77.017838]},
                               name="Test", firstname="Gurgaon waterpoint", description="This a waterpoint in Gurgaon.",
                               mobile_number="1234564")
    e.set_aggregation_path("governance", ["Commune Head", "Commune Lead", "Commune People"])
    try:
        e.save()
    except Exception:
        pass


def create_questions(unique_id_type):
    question1 = UniqueIdField(unique_id_type=unique_id_type[0], label="What is associatéd entity?", code="EID",
                              name="What is associatéd entity?", instruction="Answer must be 12 characters maximum")
    question2 = TextField(label="What is your namé?", code="NA", name="What is your namé?",
                          constraints=[TextLengthConstraint(min=1, max=10)],
                          defaultValue="some default value",
                          instruction="Answer must be a word or phrase 10 characters maximum")
    question3 = IntegerField(label="What is age öf father?", code="FA", name="What is age öf father?",
                             constraints=[NumericRangeConstraint(min=18, max=100)],
                             instruction="Answer must be a number between 18-100.")
    question4 = DateField(label="What is réporting date?", code="RD", name="What is réporting date?",
                          date_format="dd.mm.yyyy",
                          instruction="Answer must be a date in the following format: day.month.year. Example: 25.12.2011",
                          event_time_field_flag=True)
    question5 = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
                            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True,
                            instruction="Choose 1 answer from the list.")
    question6 = SelectField(label="What aré symptoms?", code="SY", name="What aré symptoms?",
                            options=[("Rapid weight loss", "a"), ("Dry cough", "b"), ("Pneumonia", "c"),
                                     ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False,
                            instruction="Choose 1 or more answers from the list.")
    question7 = GeoCodeField(name="What is the GPS code for clinic?", code="GPS",
                             label="What is the GPS code for clinic?",
                             instruction="Answer must be GPS co-ordinates in the following format: xx.xxxx,yy.yyyy Example: -18.1324,27.6547")
    question8 = SelectField(label="What are the required medicines?", code="RM", name="What are the required medicines?"
        ,
                            options=[("Hivid", "a"), ("Rétrovir", "b"), ("Vidéx EC", "c"), ("Epzicom", "d")],
                            single_select_flag=False,
                            instruction="Choose 1 or more answers from the list.", required=False)
    return [question1, question2, question3, question4, question5, question6, question7, question8]


def create_project1(entity_type, manager, questions, weekly_reminder_and_deadline):
    form_model = FormModel(manager, name="AIDS", label="Aids form_model",
                           form_code="cli001", type='survey',
                           fields=questions,
                           entity_type=entity_type
    )
    try:
        qid = form_model.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli001").delete()
        qid = form_model.save()
    project1 = Project(name="Clinic Test Project1", goals="This project is for automation", project_type="survey",
                       entity_type=entity_type[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                       sender_group="close")
    project1.qid = qid
    project1.reminder_and_deadline = weekly_reminder_and_deadline
    try:
        project1.save(manager)
    except Exception:
        pass
    reminder = Reminder(project_id=project1.id, day=2, reminder_mode=ReminderMode.BEFORE_DEADLINE,
                        organization_id='SLX364903',
                        message="2 day(s) are remainning to deadline. Please send your data for Clinic Test Project1.")
    reminder.save()
    # Create reminders for project1
    reminder = Reminder(project_id=project1.id, day=0, reminder_mode=ReminderMode.ON_DEADLINE,
                        organization_id='SLX364903',
                        message="Today is the deadline. Please send your data for Clinic Test Project1.")
    reminder.save()
    reminder = Reminder(project_id=project1.id, day=2, reminder_mode=ReminderMode.AFTER_DEADLINE,
                        organization_id='SLX364903',
                        message="2 days are overdue the deadline. Please send your data for Clinic Test Project1.")
    reminder.save()
    # Associate datasenders/reporters with project 1
    project1.data_senders.extend(["rep5", "rep6", "rep1", "rep8", "rep9", "rep3"])
    project1.save(manager)


def create_project2(CLINIC_ENTITY_TYPE, manager, questions):
    form_model2 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli002", type='survey',
                            fields=questions,
                            entity_type=CLINIC_ENTITY_TYPE)
    try:
        qid2 = form_model2.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli002").delete()
        qid2 = form_model2.save()
    project2 = Project(name="Clinic2 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                       sender_group="close")
    project2.qid = qid2
    try:
        project2.save(manager)
    except Exception:
        pass


def create_project3(CLINIC_ENTITY_TYPE, manager, questions):
    form_model3 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli003", type='survey',
                            fields=questions,
                            entity_type=CLINIC_ENTITY_TYPE)
    try:
        qid3 = form_model3.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli003").delete()
        qid3 = form_model3.save()
    project3 = Project(name="Clinic3 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                       sender_group="close")
    project3.qid = qid3
    try:
        project3.save(manager)
    except Exception:
        pass


def create_project4(CLINIC_ENTITY_TYPE, manager, questions):
    form_model4 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli004", type='survey',
                            fields=questions,
                            entity_type=CLINIC_ENTITY_TYPE)
    try:
        qid4 = form_model4.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli004").delete()
        qid4 = form_model4.save()
    project4 = Project(name="Clinic4 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                       sender_group="close")
    project4.qid = qid4
    try:
        project4.save(manager)
    except Exception:
        pass


def create_project5(CLINIC_ENTITY_TYPE, manager, questions):
    form_model5 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli005", type='survey',
                            fields=questions,
                            entity_type=CLINIC_ENTITY_TYPE)
    try:
        qid5 = form_model5.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli005").delete()
        qid5 = form_model5.save()
    project5 = Project(name="Clinic5 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                       sender_group="close")
    project5.qid = qid5
    try:
        project5.save(manager)
    except Exception:
        pass


def create_project6(CLINIC_ENTITY_TYPE, manager, questions):
    form_model6 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli006", type='survey',
                            fields=questions,
                            entity_type=CLINIC_ENTITY_TYPE)
    try:
        qid6 = form_model6.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli006").delete()
        qid6 = form_model6.save()
    project6 = Project(name="Clinic6 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                       sender_group="close")
    project6.qid = qid6
    try:
        project6.save(manager)
    except Exception:
        pass


def create_project7(CLINIC_ENTITY_TYPE, manager, questions):
    form_model7 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli007", type='survey',
                            fields=questions,
                            entity_type=CLINIC_ENTITY_TYPE)
    try:
        qid7 = form_model7.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli007").delete()
        qid7 = form_model7.save()
    project7 = Project(name="Clinic7 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                       sender_group="close")
    project7.qid = qid7
    try:
        project7.save(manager)
    except Exception:
        pass


def create_project11(CLINIC_ENTITY_TYPE, manager, questions):
    form_model11 = FormModel(manager, name="AIDS", label="Aids form_model",
                             form_code="cli011", type='survey',
                             fields=questions,
                             entity_type=CLINIC_ENTITY_TYPE
    )
    weekly_reminder_and_deadline = {
        "deadline_week": "5",
        "deadline_type": "Following",
        "has_deadline": True,
        "frequency_period": "week",
        "should_send_reminder_to_all_ds": True
    }
    try:
        qid11 = form_model11.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli011").delete()
        qid11 = form_model11.save()
    project11 = Project(name="Clinic All DS (Following)", goals="This project is for automation", project_type="survey",
                        entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                        sender_group="close")
    project11.qid = qid11
    project11.reminder_and_deadline = weekly_reminder_and_deadline
    try:
        project11.save(manager)
    except Exception:
        pass
    reminder = Reminder(project_id=project11.id, day=3, reminder_mode=ReminderMode.BEFORE_DEADLINE,
                        organization_id='SLX364903',
                        message="3 day(s) are remainning to deadline. Please send your data for Clinic All DS (Following).")
    reminder.save()
    # Create reminders for project11
    reminder = Reminder(project_id=project11.id, day=0, reminder_mode=ReminderMode.ON_DEADLINE,
                        organization_id='SLX364903',
                        message="Today is the deadline. Please send your data for Clinic All DS (Following).")
    reminder.save()
    reminder = Reminder(project_id=project11.id, day=3, reminder_mode=ReminderMode.AFTER_DEADLINE,
                        organization_id='SLX364903',
                        message="3 days are overdue the deadline. Please send your data for Clinic All DS (Following).")
    reminder.save()
    # Associate datasenders/reporters with project 1
    project11.data_senders.extend(["rep5", "rep6", "rep7"])
    project11.save(manager)


def create_project10(CLINIC_ENTITY_TYPE, manager, questions):
    form_model10 = FormModel(manager, name="AIDS", label="Aids form_model",
                             form_code="cli010", type='survey',
                             fields=questions,
                             entity_type=CLINIC_ENTITY_TYPE
    )
    weekly_reminder_and_deadline = {
        "deadline_week": "5",
        "deadline_type": "Following",
        "has_deadline": True,
        "frequency_period": "week",
        "should_send_reminder_to_all_ds": False
    }
    try:
        qid10 = form_model10.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli010").delete()
        qid10 = form_model10.save()
    project10 = Project(name="Clinic DS W/O Submission (Following)", goals="This project is for automation",
                        project_type="survey",
                        entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                        sender_group="close")
    project10.qid = qid10
    project10.reminder_and_deadline = weekly_reminder_and_deadline
    try:
        project10.save(manager)
    except Exception:
        pass
    reminder = Reminder(project_id=project10.id, day=1, reminder_mode=ReminderMode.BEFORE_DEADLINE,
                        organization_id='SLX364903',
                        message="1 day is remainning to deadline. Please send your data for Clinic DS W/O Submission (Following).")
    reminder.save()
    # Create reminders for project10
    reminder = Reminder(project_id=project10.id, day=0, reminder_mode=ReminderMode.ON_DEADLINE,
                        organization_id='SLX364903',
                        message="Today is the deadline. Please send your data for Clinic10 Test Project.")
    reminder.save()
    reminder = Reminder(project_id=project10.id, day=1, reminder_mode=ReminderMode.AFTER_DEADLINE,
                        organization_id='SLX364903',
                        message="1 day is overdue the deadline. Please send your data for Clinic DS W/O Submission (Following).")
    reminder.save()
    # Associate datasenders/reporters with project 1
    project10.data_senders.extend(["rep5", "rep6", "rep7"])
    project10.save(manager)


def create_project9(CLINIC_ENTITY_TYPE, manager, questions, weekly_reminder_and_deadline):
    form_model9 = FormModel(manager, name="AIDS Clinici", label="Aids form_model",
                            form_code="cli009", type='survey',
                            fields=questions,
                            entity_type=CLINIC_ENTITY_TYPE)
    try:
        qid = form_model9.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli009").delete()
        qid = form_model9.save()
    project9 = Project(name="Clinic9 Reminder Test Project", goals="This project is for automation",
                       project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                       sender_group="close")
    project9.qid = qid
    project9.reminder_and_deadline = weekly_reminder_and_deadline
    try:
        project9.save(manager)
    except Exception:
        pass

    # Create reminders for project2 and project 9
    reminder = Reminder(project_id=project9.id, day=0, reminder_mode=ReminderMode.ON_DEADLINE,
                        organization_id='SLX364903',
                        message="Reminder test")
    reminder.save()
    # Associate datasenders/reporters with project 9
    project9.data_senders.extend(["rep3", "rep4"])
    project9.save(manager)


def create_project8(CLINIC_ENTITY_TYPE, manager, questions):
    form_model8 = FormModel(manager, name="AIDS", label="Aids form_model",
                            form_code="cli008", type='survey',
                            fields=questions,
                            entity_type=CLINIC_ENTITY_TYPE)
    try:
        qid8 = form_model8.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli008").delete()
        qid8 = form_model8.save()
    project8 = Project(name="Clinic8 Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms"], activity_report='no', sender_group="close")
    project8.qid = qid8
    try:
        project8.save(manager)
    except Exception:
        pass


def create_project12(CLINIC_ENTITY_TYPE, manager, questions):
    form_model12 = FormModel(manager, name="AIDS", label="Aids form_model",
                             form_code="cli012", type='survey',
                             fields=questions,
                             entity_type=CLINIC_ENTITY_TYPE
    )
    weekly_reminder_and_deadline = {
        "deadline_week": "5",
        "deadline_type": "Same",
        "has_deadline": True,
        "frequency_period": "week",
        "should_send_reminder_to_all_ds": False
    }
    try:
        qid12 = form_model12.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli012").delete()
        qid12 = form_model12.save()
    project12 = Project(name="Clinic DS W/O Submission (That)", goals="This project is for automation",
                        project_type="survey",
                        entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                        sender_group="close")
    project12.qid = qid12
    project12.reminder_and_deadline = weekly_reminder_and_deadline
    try:
        project12.save(manager)
    except Exception:
        pass

    # Create reminders for project12
    reminder = Reminder(project_id=project12.id, day=4, reminder_mode=ReminderMode.BEFORE_DEADLINE,
                        organization_id='SLX364903',
                        message="4 day(s) are remainning to deadline. Please send your data for Clinic DS W/O Submission (That).")
    reminder.save()
    reminder = Reminder(project_id=project12.id, day=4, reminder_mode=ReminderMode.AFTER_DEADLINE,
                        organization_id='SLX364903',
                        message="4 day(s) are overdue the deadline. Please send your data for Clinic DS W/O Submission (That).")
    reminder.save()
    # Create reminders for project12
    reminder = Reminder(project_id=project12.id, day=0, reminder_mode=ReminderMode.ON_DEADLINE,
                        organization_id='SLX364903',
                        message="Today is the deadline. Please send your data for Clinic DS W/O Submission (That).")
    reminder.save()
    # Associate datasenders/reporters with project 1
    project12.data_senders.extend(["rep5", "rep6", "rep7"])
    project12.save(manager)


def create_project13(CLINIC_ENTITY_TYPE, manager, questions):
    form_model13 = FormModel(manager, name="AIDS", label="Aids form_model",
                             form_code="cli013", type='survey',
                             fields=questions,
                             entity_type=CLINIC_ENTITY_TYPE
    )
    monthly_reminder_and_deadline = {
        "deadline_month": "26",
        "deadline_type": "Same",
        "has_deadline": True,
        "frequency_period": "month",
        "should_send_reminder_to_all_ds": False
    }
    try:
        qid13 = form_model13.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli013").delete()
        qid13 = form_model13.save()
    project13 = Project(name="Clinic DS W/O Monthly Submission (Same)", goals="This project is for automation",
                        project_type="survey",
                        entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                        sender_group="close")
    project13.qid = qid13
    project13.reminder_and_deadline = monthly_reminder_and_deadline
    try:
        project13.save(manager)
    except Exception:
        pass

    # Create reminders for project13
    reminder = Reminder(project_id=project13.id, day=15, reminder_mode=ReminderMode.BEFORE_DEADLINE,
                        organization_id='SLX364903',
                        message="15 days are remainning to deadline. Please send your data for Clinic DS W/O Monthly Submission (Same).")
    reminder.save()
    reminder = Reminder(project_id=project13.id, day=15, reminder_mode=ReminderMode.AFTER_DEADLINE,
                        organization_id='SLX364903',
                        message="15 days are overdue the deadline. Please send your data for Clinic DS W/O Monthly Submission (Same).")
    reminder.save()
    # Create reminders for project13
    reminder = Reminder(project_id=project13.id, day=0, reminder_mode=ReminderMode.ON_DEADLINE,
                        organization_id='SLX364903',
                        message="Today is the deadline. Please send your data for Clinic DS W/O Monthly Submission (Same).")
    reminder.save()
    # Associate datasenders/reporters with project 1
    project13.data_senders.extend(["rep5", "rep6", "rep7"])
    project13.save(manager)


def create_project14(CLINIC_ENTITY_TYPE, manager, questions):
    form_model14 = FormModel(manager, name="AIDS", label="Aids form_model",
                             form_code="cli014", type='survey',
                             fields=questions,
                             entity_type=CLINIC_ENTITY_TYPE
    )
    monthly_reminder_and_deadline = {
        "deadline_month": "26",
        "deadline_type": "Following",
        "has_deadline": True,
        "frequency_period": "month",
        "should_send_reminder_to_all_ds": False
    }
    try:
        qid14 = form_model14.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli014").delete()
        qid14 = form_model14.save()
    project14 = Project(name="Clinic DS W/O Monthly Submission (following)", goals="This project is for automation",
                        project_type="survey",
                        entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                        sender_group="close")
    project14.qid = qid14
    project14.reminder_and_deadline = monthly_reminder_and_deadline
    try:
        project14.save(manager)
    except Exception:
        pass

    # Create reminders for project14
    reminder = Reminder(project_id=project14.id, day=10, reminder_mode=ReminderMode.BEFORE_DEADLINE,
                        organization_id='SLX364903',
                        message="10 days are remainning to deadline. Please send your data for Clinic DS W/O Monthly Submission (following).")
    reminder.save()
    reminder = Reminder(project_id=project14.id, day=10, reminder_mode=ReminderMode.AFTER_DEADLINE,
                        organization_id='SLX364903',
                        message="10 days are overdue the deadline. Please send your data for Clinic DS W/O Monthly Submission (following).")
    reminder.save()
    # Create reminders for project14
    reminder = Reminder(project_id=project14.id, day=0, reminder_mode=ReminderMode.ON_DEADLINE,
                        organization_id='SLX364903',
                        message="Today is the deadline. Please send your data for Clinic DS W/O Monthly Submission (following).")
    reminder.save()
    # Associate datasenders/reporters with project 1
    project14.data_senders.extend(["rep5", "rep6", "rep7"])
    project14.save(manager)


def create_project15(CLINIC_ENTITY_TYPE, manager, questions):
    form_model15 = FormModel(manager, name="AIDS", label="Aids form_model",
                             form_code="cli015", type='survey',
                             fields=questions,
                             entity_type=CLINIC_ENTITY_TYPE
    )
    monthly_reminder_and_deadline = {
        "deadline_month": "26",
        "deadline_type": "Following",
        "has_deadline": True,
        "frequency_period": "month",
        "should_send_reminder_to_all_ds": True
    }
    try:
        qid15 = form_model15.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli015").delete()
        qid15 = form_model15.save()
    project15 = Project(name="Clinic All DS Monthly Submission (following)", goals="This project is for automation",
                        project_type="survey",
                        entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                        sender_group="close")
    project15.qid = qid15
    project15.reminder_and_deadline = monthly_reminder_and_deadline
    try:
        project15.save(manager)
    except Exception:
        pass

    # Create reminders for project15
    reminder = Reminder(project_id=project15.id, day=5, reminder_mode=ReminderMode.BEFORE_DEADLINE,
                        organization_id='SLX364903',
                        message="5 days are remainning to deadline. Please send your data for Clinic All DS Monthly Submission (following).")
    reminder.save()
    reminder = Reminder(project_id=project15.id, day=5, reminder_mode=ReminderMode.AFTER_DEADLINE,
                        organization_id='SLX364903',
                        message="5 days are overdue the deadline. Please send your data for Clinic All DS Monthly Submission (following).")
    reminder.save()
    # Create reminders for project15
    reminder = Reminder(project_id=project15.id, day=0, reminder_mode=ReminderMode.ON_DEADLINE,
                        organization_id='SLX364903',
                        message="Today is the deadline. Please send your data for Clinic All DS Monthly Submission (following).")
    reminder.save()
    # Associate datasenders/reporters with project 1
    project15.data_senders.extend(["rep5", "rep6", "rep7"])
    project15.save(manager)


def create_project16(CLINIC_ENTITY_TYPE, manager, questions):
    form_model16 = FormModel(manager, name="AIDS", label="Aids form_model",
                             form_code="cli016", type='survey',
                             fields=questions,
                             entity_type=CLINIC_ENTITY_TYPE
    )
    monthly_reminder_and_deadline = {
        "deadline_month": "26",
        "deadline_type": "Same",
        "has_deadline": True,
        "frequency_period": "month",
        "should_send_reminder_to_all_ds": "True"
    }
    try:
        qid16 = form_model16.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli016").delete()
        qid16 = form_model16.save()
    project16 = Project(name="Clinic All DS Monthly Submission (that)", goals="This project is for automation",
                        project_type="survey",
                        entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                        sender_group="close")
    project16.qid = qid16
    project16.reminder_and_deadline = monthly_reminder_and_deadline
    try:
        project16.save(manager)
    except Exception:
        pass

    # Create reminders for project16
    reminder = Reminder(project_id=project16.id, day=2, reminder_mode=ReminderMode.BEFORE_DEADLINE,
                        organization_id='SLX364903',
                        message="2 days are remainning to deadline. Please send your data for Clinic All DS Monthly Submission (that).")
    reminder.save()
    reminder = Reminder(project_id=project16.id, day=2, reminder_mode=ReminderMode.AFTER_DEADLINE,
                        organization_id='SLX364903',
                        message="2 days are overdue the deadline. Please send your data for Clinic All DS Monthly Submission (that).")
    reminder.save()
    # Create reminders for project16
    reminder = Reminder(project_id=project16.id, day=0, reminder_mode=ReminderMode.ON_DEADLINE,
                        organization_id='SLX364903',
                        message="Today is the deadline. Please send your data for Clinic All DS Monthly Submission (that).")
    reminder.save()
    # Associate datasenders/reporters with project 1
    project16.data_senders.extend(["rep5", "rep6", "rep7"])
    project16.save(manager)


def create_project17(CLINIC_ENTITY_TYPE, manager, questions_):
    form_model17 = FormModel(manager, name="AIDS", label="Aids form_model",
                             form_code="cli017", type='survey',
                             fields=questions_,
                             entity_type=CLINIC_ENTITY_TYPE)
    try:
        qid17 = form_model17.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli017").delete()
        qid17 = form_model17.save()
    project17 = Project(name="Clinic13 Test Project", goals="This project is for automation", project_type="survey",
                        entity_type='clinic', devices=["sms", "web", "smartPhone"], activity_report='yes',
                        sender_group="close")
    project17.qid = qid17
    try:
        project17.save(manager)
    except Exception:
        pass


def create_project18(CLINIC_ENTITY_TYPE, manager, questions_):
    form_model18 = FormModel(manager, name="AIDS", label="Aids form_model",
                             form_code="cli018", type='survey',
                             fields=questions_,
                             entity_type=CLINIC_ENTITY_TYPE)
    try:
        qid18 = form_model18.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli018").delete()
        qid18 = form_model18.save()
    project18 = Project(name="Test data sorting", goals="This project is for automation", project_type="survey",
                        entity_type='clinic', devices=["sms", "web", "smartPhone"], activity_report='yes',
                        sender_group="close")
    project18.qid = qid18
    try:
        project18.save(manager)
    except Exception:
        pass


def create_project19(ENTITY_TYPE, manager):
    questions_ = create_questions(ENTITY_TYPE)
    form_model19 = FormModel(manager, name="AIDS", label="Aids form_model",
                             form_code="peo019", type='survey',
                             fields=questions_,
                             entity_type=ENTITY_TYPE)
    try:
        qid19 = form_model19.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "peo019").delete()
        qid19 = form_model19.save()
    project19 = Project(name="Project having people as subject", goals="This project is for automation",
                        project_type="survey",
                        entity_type='people', devices=["sms", "web", "smartPhone"], activity_report='no',
                        sender_group="close")
    project19.qid = qid19
    try:
        project19.save(manager)
    except Exception:
        pass


def create_clinic_project_with_monthly_reporting_period(CLINIC_ENTITY_TYPE, manager):
    clinic_code = "cli00_mp"
    project_name = "Clinic Test Project With Monthly Reporting Period"

    question1 = UniqueIdField(unique_id_type=CLINIC_ENTITY_TYPE[0],label="What is associatéd entity?", code="EID", name="What is associatéd entity?",
                              instruction="Answer must be 12 characters maximum")
    question2 = DateField(label="What is réporting date?", code="RD", name="What is réporting date?",
                          date_format="mm.yyyy",
                          instruction="Answer must be a date in the following format: day.month.year. Example: 25.12.2011",
                          event_time_field_flag=True)

    form_model = FormModel(manager, name="AIDS", label="Aids form_model",
                           form_code=clinic_code, type='survey',
                           fields=[question1, question2],
                           entity_type=CLINIC_ENTITY_TYPE
    )
    try:
        qid = form_model.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, clinic_code).delete()
        qid = form_model.save()
    project = Project(name=project_name, goals="This project is for automation", project_type="survey",
                      entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                      sender_group="close")
    project.qid = qid
    try:
        project.save(manager)
    except Exception:
        pass


def create_clinic_projects(entity_type, manager):
    organization = Organization.objects.get(pk='SLX364903')
    Reminder.objects.filter(organization=organization).delete()
    questions = create_questions(entity_type)

    weekly_reminder_and_deadline = {
        "deadline_week": "5",
        "deadline_type": "Same",
        "has_deadline": True,
        "frequency_period": "week",
        "should_send_reminder_to_all_ds": True
    }

    create_project1(entity_type, manager, questions, weekly_reminder_and_deadline)
    create_project2(entity_type, manager, questions)
    create_project3(entity_type, manager, questions[:7])
    create_project4(entity_type, manager, questions[:7])
    create_project5(entity_type, manager, questions[:7])
    create_project6(entity_type, manager, questions[:7])
    create_project7(entity_type, manager, questions[:7])
    create_project8(entity_type, manager, questions[:7])
    create_project9(entity_type, manager, questions, weekly_reminder_and_deadline)
    create_project10(entity_type, manager, questions)
    create_project11(entity_type, manager, questions)
    create_project12(entity_type, manager, questions)
    create_project13(entity_type, manager, questions)
    create_project14(entity_type, manager, questions)
    create_project15(entity_type, manager, questions)
    create_project16(entity_type, manager, questions)
    create_project17(entity_type, manager, questions[:6])

    questions_for_018 = questions[:]
    questions_for_018.pop()
    questions_for_018.pop(5)
    questions_for_018.pop(2)
    create_project18(entity_type, manager, questions_for_018)
    create_clinic_project_with_monthly_reporting_period(entity_type, manager)


def load_web_data_for_cli001(manager):
    web_player = WebPlayerV2(manager)
    text = {'form_code': 'cli001', 'EID': 'cid001', 'NA': 'Mr. Admin', 'FA': '58', 'RD': '28.02.2011', 'BG': 'c',
            'SY': 'ade', 'GPS': '79.2,20.34567', 'RM': 'a'}
    web_transport_info = TransportInfo(transport="web", source="tester150411@gmail.com", destination="")
    web_player.add_survey_response(Request(message=text, transportInfo=web_transport_info), 'rep276')


def load_web_data_for_cli018(manager):
    web_player = WebPlayerV2(manager)
    web_transport_info = TransportInfo(transport="web", source="tester150411@gmail.com", destination="")
    text = {'form_code': 'cli018', 'EID': 'cid001', 'NA': 'cat, dog', 'RD': '11.03.2010', 'BG': 'c', 'GPS': '12,14'}
    web_player.add_survey_response(Request(message=text, transportInfo=web_transport_info), 'rep276')
    text = {'form_code': 'cli018', 'EID': 'cid001', 'NA': '12, 34', 'RD': '20.02.2011', 'BG': 'd', 'GPS': '39,14'}
    web_player.add_survey_response(Request(message=text, transportInfo=web_transport_info), 'rep276')
    text = {'form_code': 'cli018', 'EID': 'cid001', 'NA': '-12, 34', 'RD': '25.12.2010', 'BG': 'a', 'GPS': '5.10,50.12'}
    web_player.add_survey_response(Request(message=text, transportInfo=web_transport_info), 'rep276')
    text = {'form_code': 'cli018', 'EID': 'cid001', 'NA': '20, 34', 'RD': '11.06.2012', 'BG': 'b', 'GPS': '21.16,14.3'}
    web_player.add_survey_response(Request(message=text, transportInfo=web_transport_info), 'rep276')


def load_sms_data_for_cli018(manager):
    JAN = datetime(2011, 01, 05, hour=12, minute=00, second=00, tzinfo=UTC)
    FEB = datetime(2011, 02, 28, hour=12, minute=00, second=00, tzinfo=UTC)
    MARCH = datetime(2011, 03, 11, tzinfo=UTC)
    APR = datetime(2011, 04, 01, tzinfo=UTC)
    DEC_2010 = datetime(2010, 12, 28, hour=00, minute=00, second=59, tzinfo=UTC)
    NOV_2010 = datetime(2010, 11, 26, hour=23, minute=59, second=59, tzinfo=UTC)

    sms_player = SMSPlayerV2(manager, [])

    FROM_NUMBER = '1234567890'
    TO_NUMBER = '919880734937'
    transport = TransportInfo(SMS, FROM_NUMBER, TO_NUMBER)

    mangrove_request = Request("cli018 .EID cid001 .NA 12.2012 .RD 15.01.2011 .BG a .GPS 16.34,11.26", transport)
    response = sms_player.add_survey_response(mangrove_request)

    datetime_mocker = DateTimeMocker()
    datetime_mocker.set_date_time_now(JAN)
    mangrove_request = Request("cli018 .EID cid001 .NA 123 .RD 10.02.2012 .BG b .GPS 61.10,58.99", transport)
    response = sms_player.add_survey_response(mangrove_request)

    datetime_mocker.set_date_time_now(FEB)
    mangrove_request = Request("cli018 .EID cid001 .NA 456 .RD 25.12.2012 .BG d .GPS 65.24,28.45", transport)
    response = sms_player.add_survey_response(mangrove_request)

    datetime_mocker.set_date_time_now(MARCH)
    mangrove_request = Request("cli018 .EID cid003 .NA cat .RD 15.10.2011 .BG c .GPS 56.34,11.00", transport)
    response = sms_player.add_survey_response(mangrove_request)

    datetime_mocker.set_date_time_now(APR)
    mangrove_request = Request("cli018 .EID cid004 .NA 2012.01.14 .RD 25.06.2011 .BG d .GPS 16.34,11.76", transport)
    response = sms_player.add_survey_response(mangrove_request)

    datetime_mocker.set_date_time_now(NOV_2010)
    mangrove_request = Request("cli018 .EID cid005 .NA 2011.12.12 .RD 04.09.2010 .BG d .GPS 10.12,11.13", transport)
    response = sms_player.add_survey_response(mangrove_request)

    datetime_mocker.set_date_time_now(DEC_2010)
    mangrove_request = Request('cli018 .EID cid001 .NA 12.23.2011 .RD 25.01.2011 .BG a .GPS 11.23,17.66', transport)
    response = sms_player.add_survey_response(mangrove_request)


def load_sms_data_for_cli001(manager):
    FEB = datetime(2011, 02, 28, hour=12, minute=00, second=00, tzinfo=UTC)
    MARCH = datetime(2011, 03, 01, tzinfo=UTC)
    DEC_2010 = datetime(2010, 12, 28, hour=00, minute=00, second=59, tzinfo=UTC)
    NOV_2010 = datetime(2010, 11, 26, hour=23, minute=59, second=59, tzinfo=UTC)
    today = datetime.today()
    LAST_WEEK = today - timedelta(days=7)
    THIS_MONTH = datetime(today.year, today.month, 1, 12, 45, 58)
    PREV_MONTH = THIS_MONTH - timedelta(days=6)
    sms_player = SMSPlayer(manager, LocationBridge(get_location_tree(), get_loc_hierarchy=get_location_hierarchy))

    FROM_NUMBER = '1234567890'
    TO_NUMBER = '919880734937'
    transport = TransportInfo(SMS, FROM_NUMBER, TO_NUMBER)

    mangrove_request = Request("cli .q1 Clinic .q2 Analalava .q3 Analalava .q4 -14.6333,47.7667 .q5 987654321",
                               transport)
    sms_player.accept(mangrove_request)

    mangrove_request = Request("cli .q1 Clinic .q2 Andapa .q3 Andapa .q4 -14.65,49.6167 .q5 87654322", transport)
    sms_player.accept(mangrove_request)

    mangrove_request = Request("cli .q1 Clinic .q2 Antalaha .q3 Antalaha .q4 -14.8833,50.25 .q5 87654323", transport)
    sms_player.accept(mangrove_request)

    mangrove_request = Request("cli .q1 Clinic .q2 ANALAMANGA .q3 ANALAMANGA .q4 -18.8,47.4833 .q5 87654324", transport)
    response = sms_player.accept(mangrove_request)

    mangrove_request = Request(
        "cli .q1 Clinic .q2 TSIMANARIRAZANA .q3 TSIMANARIRAZANA .q4 -12.35,49.3 .q5 87654325", transport)
    response = sms_player.accept(mangrove_request)
    mangrove_request = Request(
        "cli .q1 Clinic .q2 Antsirabe .q3 Antsirabe .q4 -19.8167,47.0667 .q5 87654326", transport)
    response = sms_player.accept(mangrove_request)
    mangrove_request = Request(
        "cli .q1 Clinic .q2 Besalampy .q3 Besalampy .q4 -16.75,44.5 .q5 87654327", transport)
    response = sms_player.accept(mangrove_request)
    mangrove_request = Request(
        "cli .q1 Clinic .q2 Farafangana .q3 Farafangana .q4 -22.8,47.8333 .q5 87654328", transport)
    response = sms_player.accept(mangrove_request)
    mangrove_request = Request(
        "cli .q1 Clinic .q2 Fianarantsoa-I .q3 Fianarantsoa-I .q4 -21.45,47.1 .q5 87654329", transport)
    response = sms_player.accept(mangrove_request)
    mangrove_request = Request(
        "cli .q1 Clinic .q2 Sainte-Marie .q3 Sainte-Marie .q4 -17.0833,49.8167 .q5 87654330", transport)
    response = sms_player.accept(mangrove_request)
    mangrove_request = Request(
        "cli .q1 Clinic .q2 Mahajanga .q3 Mahajanga .q4 -15.6667,46.35 .q5 87654331", transport)
    response = sms_player.accept(mangrove_request)

    datetime_mocker = DateTimeMocker()
    datetime_mocker.set_date_time_now(FEB)
    # Total number of identical records = 3
    sms_player_v2 = SMSPlayerV2(manager, [])
    mangrove_request = Request(
        "cli001 .EID cid001 .NA Mr. Tessy .FA 58 .RD 28.02.2011 .BG c .SY ade .GPS 79.2,20.34567 .RM a", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cid002 .NA Mr. Adam .FA 62 .RD 15.02.2011 .BG a .SY ab .GPS 74.2678,23.3567 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cid003 .NA Ms. Beth .FA 75 .RD 09.02.2011 .BG b .SY bc .GPS 18.245,29.3123 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    datetime_mocker.set_date_time_now(MARCH)
    # Total number of identical records = 4
    mangrove_request = Request(
        "cli001 .EID cid004 .NA Jannita .FA 90 .RD 07.03.2011 .BG b .SY bbe .GPS 45.233,28.3324 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cid005 .NA Aanda .FA 58 .RD 12.03.2011 .BG c .SY bd .GPS 40.2,69.3123 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        'cli001 .EID cid001 .NA Ianda (",) .FA 34 .RD 27.03.2011 .BG d .SY be .GPS 38.3452,15.3345 .RM b', transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cid001 .NA ànita .FA 45 .RD 07.03.2011 .BG b .SY bbe .GPS 45.233,28.3324 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cid004 .NA Amanda .FA 81 .RD 12.03.2011 .BG c .SY bd .GPS 40.2,69.3123 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        'cli001 .EID cid005 .NA Vanda (",) .FA 34 .RD 27.03.2011 .BG d .SY be .GPS 38.3452,15.3345 .RM b', transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cid003 .NA ànnita .FA 80 .RD 07.03.2011 .BG b .SY bbe .GPS 45.233,28.3324 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cid002 .NA Amanda .FA 69 .RD 12.03.2011 .BG c .SY bd .GPS 40.2,69.3123 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        'cli001 .EID cid004 .NA Panda (",) .FA 34 .RD 27.03.2011 .BG d .SY be .GPS 38.3452,15.3345 .RM b', transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cid005 .NA ànnita .FA 50 .RD 07.03.2011 .BG b .SY bbe .GPS 45.233,28.3324 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cid003 .NA Jimanda .FA 86 .RD 12.03.2011 .BG c .SY bd .GPS 40.2,69.3123 .RM ac", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        'cli001 .EID cli10 .NA Kanda (",) .FA 64 .RD 27.03.2011 .BG d .SY be .GPS 38.3452,15.3345 .RM b', transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cid004 .NA ànnita .FA 30 .RD 07.03.2011 .BG b .SY bbe .GPS 45.233,28.3324 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cid005 .NA Qamanda  .FA 47 .RD 12.03.2011 .BG c .SY bd .GPS 40.2,69.3123 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        'cli001 .EID cid001 .NA Huanda (*_*) .FA 74 .RD 27.03.2011 .BG d .SY be .GPS 38.3452,15.3345 .RM b', transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    datetime_mocker.set_date_time_now(DEC_2010)
    # Total number of identical records = 4
    mangrove_request = Request(
        "cli001 .EID cli12 .NA Jugal .FA 47 .RD 15.12.2010 .BG d .SY ace .GPS -58.3452,19.3345 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli11 .NA De'melo .FA 38 .RD 27.12.2010 .BG c .SY ba .GPS 81.672,92.33456 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli13 .NA Dono`mova .FA 24 .RD 06.12.2010 .BG b .SY cd .GPS 65.23452,-28.3456 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli15 .NA Aàntra .FA 89 .RD 11.12.2010 .BG a .SY bd .GPS 45.234,89.32345 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    datetime_mocker.set_date_time_now(NOV_2010)
    # Total number of identical records = 3
    mangrove_request = Request(
        "cli001 .EID cli12 .NA ànnita .FA 90 .RD 07.11.2010 .BG b .SY bbe .GPS 45.233,28.3324 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli14 .NA Amanda .FA 67 .RD 12.11.2010 .BG c .SY bd .GPS 40.2,69.3123 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        'cli001 .EID cli8 .NA Kanda (",) .FA 34 .RD 27.11.2010 .BG d .SY be .GPS 38.3452,15.3345 .RM b', transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli9 .NA ànnita .FA 90 .RD 17.11.2010 .BG b .SY bbe .GPS 45.233,28.3324 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cid007 .NA Amanda .FA 73 .RD 12.11.2010 .BG c .SY bd .GPS 40.2,69.3123 .RM b", transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        'cli001 .EID cli8 .NA Kanda (",) .FA 34 .RD 27.11.2010 .BG d .SY be .GPS 38.3452,15.3345 .RM b', transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    datetime_mocker.set_date_time_now(PREV_MONTH)
    month = today.month - 1
    year = today.year
    if not (month):
        month = 12
        year = today.year - 1
    Last_month_date = "12." + str(month) + "." + str(year)
    # Total number of identical records = 4
    mangrove_request = Request(
        "cli001 .EID cli9 .NA Demelo .FA 38 .RD " + Last_month_date + " .BG c .SY ba .GPS 19.672,92.33456 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli10 .NA Zorro .FA 48 .RD " + Last_month_date + " .BG b .SY cd .GPS 23.23452,-28.3456 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli11 .NA Aàntra .FA 98 .RD " + Last_month_date + " .BG a .SY cb .GPS -45.234,89.32345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli12 .NA ànnita .FA 37 .RD " + Last_month_date + " .BG d .SY cbe .GPS -78.233,-28.3324 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli9 .NA Demelo .FA 38 .RD " + Last_month_date + " .BG c .SY ba .GPS 19.672,92.33456 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli10 .NA Zorro .FA 48 .RD " + Last_month_date + " .BG b .SY cd .GPS 23.23452,-28.3456 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli11 .NA Aàntra .FA 95 .RD " + Last_month_date + " .BG a .SY cb .GPS -45.234,89.32345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli12 .NA ànnita .FA 35 .RD " + Last_month_date + " .BG d .SY cbe .GPS -78.233,-28.3324 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli9 .NA Demelo .FA 32 .RD " + Last_month_date + " .BG c .SY ba .GPS 19.672,92.33456 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli10 .NA Zorro .FA 43 .RD " + Last_month_date + " .BG b .SY cd .GPS 23.23452,-28.3456 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli11 .NA Aàntra .FA 91 .RD " + Last_month_date + " .BG a .SY be .GPS -45.234,89.32345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli12 .NA ànnita .FA 45 .RD " + Last_month_date + " .BG d .SY cbe .GPS -78.233,-28.3324 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    datetime_mocker.set_date_time_now(THIS_MONTH)
    current_month_date = "01." + str(today.month) + "." + str(today.year)
    # Total number of identical records = 4
    mangrove_request = Request(
        "cli001 .EID cli13 .NA Dmanda .FA 69 .RD " + current_month_date + " .BG c .SY ce .GPS 40.2,69.3123 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli14 .NA Vamand .FA 36 .RD " + current_month_date + " .BG a .SY ace .GPS 58.3452,115.3345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli15 .NA M!lo .FA 88 .RD " + current_month_date + " .BG b .SY ba .GPS 19.672,92.33456 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli16 .NA K!llo .FA 88 .RD " + current_month_date + " .BG a .SY ac .GPS 19.672,92.33456 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli13 .NA Dmanda .FA 89 .RD " + current_month_date + " .BG c .SY ce .GPS 40.2,69.3123 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli14 .NA Vamand .FA 56 .RD " + current_month_date + " .BG a .SY ace .GPS 58.3452,115.3345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli15 .NA M!lo .FA 45 .RD " + current_month_date + " .BG c .SY ca .GPS 19.672,92.33456 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli16 .NA K!llo .FA 28 .RD " + current_month_date + " .BG b .SY ae .GPS 19.672,92.33456 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    datetime_mocker.end_mock()

    today_date = str(today.day) + "." + str(today.month) + "." + str(today.year)
    # Total number of identical records = 3
    mangrove_request = Request(
        "cli001 .EID cli17 .NA Catty .FA 78 .RD " + today_date + " .BG b .SY dce .GPS 33.23452,-68.3456 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli18 .NA àntra .FA 28 .RD " + today_date + " .BG a .SY adb .GPS -45.234,169.32345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli9 .NA Tinnita .RD " + today_date + " .FA 37 .BG d .SY ace .GPS -78.233,-28.3324 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    mangrove_request = Request(
        "cli001 .EID cli17 .NA Catty .FA 98 .RD " + today_date + " .BG b .SY dce .GPS 33.23452,-68.3456 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli18 .NA àntra .FA 58 .RD " + today_date + " .BG a .SY adb .GPS -45.234,169.32345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli001 .EID cli9 .NA Tinnita .RD " + today_date + " .FA 27 .BG d .SY ace .GPS -78.233,-28.3324 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    FROM_NUMBER = '919970059125'
    TO_NUMBER = '919880734937'
    transport = TransportInfo(SMS, FROM_NUMBER, TO_NUMBER)

    datetime_mocker2 = DateTimeMocker()
    datetime_mocker2.set_date_time_now(LAST_WEEK)
    last_week_date = str(LAST_WEEK.day) + "." + str(LAST_WEEK.month) + "." + str(LAST_WEEK.year)
    # Total number of identical records = 4
    mangrove_request = Request(
        "cli010 .EID cli13 .NA Dmanda .FA 69 .RD " + last_week_date + " .BG c .SY ce .GPS 40.2,69.3123 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli010 .EID cli14 .NA Vamand .FA 36 .RD " + last_week_date + " .BG a .SY ace .GPS 58.3452,115.3345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli010 .EID cli15 .NA M!lo .FA 88 .RD " + last_week_date + " .BG b .SY ba .GPS 19.672,92.33456 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    # Total number of identical records = 4
    mangrove_request = Request(
        "cli012 .EID cli13 .NA Dmanda .FA 69 .RD " + last_week_date + " .BG c .SY ce .GPS 40.2,69.3123 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli012 .EID cli14 .NA Vamand .FA 36 .RD " + last_week_date + " .BG a .SY ace .GPS 58.3452,115.3345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli012 .EID cli15 .NA M!lo .FA 88 .RD " + last_week_date + " .BG b .SY ba .GPS 19.672,92.33456 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    # Total number of identical records = 4
    mangrove_request = Request(
        "cli011 .EID cli13 .NA Dmanda .FA 69 .RD " + last_week_date + " .BG c .SY ce .GPS 40.2,69.3123 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli011 .EID cli14 .NA Vamand .FA 36 .RD " + last_week_date + " .BG a .SY ace .GPS 58.3452,115.3345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli011 .EID cli15 .NA M!lo .FA 88 .RD " + last_week_date + " .BG b .SY ba .GPS 19.672,92.33456 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    FROM_NUMBER = '919970059125'
    TO_NUMBER = '919880734937'
    transport = TransportInfo(SMS, FROM_NUMBER, TO_NUMBER)

    datetime_mocker2.set_date_time_now(PREV_MONTH)
    last_week_date = str(PREV_MONTH.day) + "." + str(PREV_MONTH.month) + "." + str(PREV_MONTH.year)
    # Total number of identical records = 3
    mangrove_request = Request(
        "cli013 .EID cli13 .NA Dmanda .FA 69 .RD " + last_week_date + " .BG c .SY ce .GPS 40.2,69.3123 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli013 .EID cli14 .NA Vamand .FA 36 .RD " + last_week_date + " .BG a .SY ace .GPS 58.3452,115.3345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli013 .EID cli15 .NA M!lo .FA 88 .RD " + last_week_date + " .BG b .SY ba .GPS 19.672,92.33456 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    # Total number of identical records = 3
    mangrove_request = Request(
        "cli015 .EID cli13 .NA Dmanda .FA 69 .RD " + last_week_date + " .BG c .SY ce .GPS 40.2,69.3123 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli015 .EID cli14 .NA Vamand .FA 36 .RD " + last_week_date + " .BG a .SY ace .GPS 58.3452,115.3345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli015 .EID cli15 .NA M!lo .FA 88 .RD " + last_week_date + " .BG b .SY ba .GPS 19.672,92.33456 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    # Total number of identical records = 3
    mangrove_request = Request(
        "cli014 .EID cli13 .NA Dmanda .FA 69 .RD " + last_week_date + " .BG c .SY ce .GPS 40.2,69.3123 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli014 .EID cli14 .NA Vamand .FA 36 .RD " + last_week_date + " .BG a .SY ace .GPS 58.3452,115.3345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli014 .EID cli15 .NA M!lo .FA 88 .RD " + last_week_date + " .BG b .SY ba .GPS 19.672,92.33456 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    # Total number of identical records = 3
    mangrove_request = Request(
        "cli016 .EID cli13 .NA Dmanda .FA 69 .RD " + last_week_date + " .BG c .SY ce .GPS 40.2,69.3123 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli016 .EID cli14 .NA Vamand .FA 36 .RD " + last_week_date + " .BG a .SY ace .GPS 58.345,115.3345 .RM b",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli016 .EID cli15 .NA M!lo .FA 88 .RD " + last_week_date + " .BG b .SY ba .GPS 19.672,92.33456 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    FROM_NUMBER = '917798987102'
    TO_NUMBER = '919880734937'
    transport = TransportInfo(SMS, FROM_NUMBER, TO_NUMBER)

    datetime_mocker2.set_date_time_now(THIS_MONTH)

    this_month = str(THIS_MONTH.day) + "." + str(THIS_MONTH.month) + "." + str(THIS_MONTH.year)
    # Total number of identical records = 3
    mangrove_request = Request(
        "cli013 .EID cli16 .NA Catty .FA 78 .RD " + this_month + " .BG b .SY dce .GPS 33.23452,-68.3456 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli013 .EID cli17 .NA àntra .FA 28 .RD " + this_month + " .BG a .SY adb .GPS -45.234,169.32345 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli013 .EID cli18 .NA Tinnita .RD " + this_month + " .FA 37 .BG d .SY ace .GPS -78.233,-28.3324 .RM d",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    # Total number of identical records = 3
    mangrove_request = Request(
        "cli014 .EID cli16 .NA Catty .FA 78 .RD " + this_month + " .BG b .SY dce .GPS 33.23452,-68.3456 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli014 .EID cli17 .NA àntra .FA 28 .RD " + this_month + " .BG a .SY adb .GPS -45.234,169.32345 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli014 .EID cli18 .NA Tinnita .RD " + this_month + " .FA 37 .BG d .SY ace .GPS -78.233,-28.3324 .RM d",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    # Total number of identical records = 3
    mangrove_request = Request(
        "cli015 .EID cli16 .NA Catty .FA 78 .RD " + this_month + " .BG b .SY dce .GPS 33.23452,-68.3456 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli015 .EID cli17 .NA àntra .FA 28 .RD " + this_month + " .BG a .SY adb .GPS -45.234,169.32345 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli015 .EID cli18 .NA Tinnita .RD " + this_month + " .FA 37 .BG d .SY ace .GPS -78.233,-28.3324 .RM d",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    # Total number of identical records = 3
    mangrove_request = Request(
        "cli016 .EID cli16 .NA Catty .FA 78 .RD " + this_month + " .BG b .SY dce .GPS 33.23452,-68.3456 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli016 .EID cli17 .NA àntra .FA 28 .RD " + this_month + " .BG a .SY adb .GPS -45.234,169.32345 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli016 .EID cli18 .NA Tinnita .RD " + this_month + " .FA 37 .BG d .SY ace .GPS -78.233,-28.3324 .RM d",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    datetime_mocker2.end_mock()

    FROM_NUMBER = '917798987102'
    TO_NUMBER = '919880734937'
    transport = TransportInfo(SMS, FROM_NUMBER, TO_NUMBER)

    today_date = str(today.day) + "." + str(today.month) + "." + str(today.year)
    # Total number of identical records = 3
    mangrove_request = Request(
        "cli010 .EID cli16 .NA Catty .FA 78 .RD " + today_date + " .BG b .SY dce .GPS 33.23452,-68.3456 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli010 .EID cli17 .NA àntra .FA 28 .RD " + today_date + " .BG a .SY adb .GPS -45.234,169.32345 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli010 .EID cli18 .NA Tinnita .RD " + today_date + " .FA 37 .BG d .SY ace .GPS -78.233,-28.3324 .RM d",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    # Total number of identical records = 3
    mangrove_request = Request(
        "cli011 .EID cli16 .NA Catty .FA 78 .RD " + today_date + " .BG b .SY dce .GPS 33.23452,-68.3456 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli011 .EID cli17 .NA àntra .FA 28 .RD " + today_date + " .BG a .SY adb .GPS -45.234,169.32345 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli011 .EID cli18 .NA Tinnita .RD " + today_date + " .FA 37 .BG d .SY ace .GPS -78.233,-28.3324 .RM d",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)

    # Total number of identical records = 3
    mangrove_request = Request(
        "cli012 .EID cli16 .NA Catty .FA 78 .RD " + today_date + " .BG b .SY dce .GPS 33.23452,-68.3456 .RM a",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli012 .EID cli17 .NA àntra .FA 28 .RD " + today_date + " .BG a .SY adb .GPS -45.234,169.32345 .RM c",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)
    mangrove_request = Request(
        "cli012 .EID cli18 .NA Tinnita .RD " + today_date + " .FA 37 .BG d .SY ace .GPS -78.233,-28.3324 .RM d",
        transport)
    response = sms_player_v2.add_survey_response(mangrove_request)


def create_clinic_project_for_trial_account(CLINIC_ENTITY_TYPE, manager, trial_org_pk, register_a_datasender):
    organization = Organization.objects.get(pk=trial_org_pk)
    question1 = UniqueIdField(unique_id_type=CLINIC_ENTITY_TYPE[0],label="entity_question", code="EID", name="What is associatéd entity?",
                          instruction="Answer must be 12 characters maximum")
    question2 = TextField(label="Name", code="NA", name="What is your namé?",
                          constraints=[TextLengthConstraint(min=1, max=10)],
                          defaultValue="some default value",
                          instruction="Answer must be a word or phrase 10 characters maximum")
    question3 = IntegerField(label="Father age", code="FA", name="What is age öf father?",
                             constraints=[NumericRangeConstraint(min=18, max=100)],
                             instruction="Answer must be a number between 18-100.")
    question4 = DateField(label="Report date", code="RD", name="What is réporting date?",
                          date_format="dd.mm.yyyy",
                          instruction="Answer must be a date in the following format: day.month.year. Example: 25.12.2011")
    question5 = SelectField(label="Blood Group", code="BG", name="What is your blood group?",
                            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True,
                            instruction="Choose 1 answer from the list.")
    question6 = SelectField(label="Symptoms", code="SY", name="What aré symptoms?",
                            options=[("Rapid weight loss", "a"), ("Dry cough", "b"), ("Pneumonia", "c"),
                                     ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False,
                            instruction="Choose 1 or more answers from the list.")
    question7 = GeoCodeField(name="What is the GPS codé for clinic", code="GPS",
                             label="What is the GPS code for clinic?",
                             instruction="Answer must be GPS co-ordinates in the following format: xx.xxxx,yy.yyyy Example: -18.1324,27.6547")
    question8 = SelectField(label="Required Medicines", code="RM", name="What are the required medicines?",
                            options=[("Hivid", "a"), ("Rétrovir", "b"), ("Vidéx EC", "c"), ("Epzicom", "d")],
                            single_select_flag=False,
                            instruction="Choose 1 or more answers from the list.", required=False)
    form_model = FormModel(manager, name="AIDS", label="Aids form_model",
                           form_code="cli051", type='survey',
                           fields=[question1, question2, question3, question4, question5, question6, question7,
                                   question8],
                           entity_type=CLINIC_ENTITY_TYPE
    )

    weekly_reminder_and_deadline = {
        "deadline_week": "5",
        "deadline_type": "Same",
        "has_deadline": True,
        "frequency_period": "week",
        "should_send_reminder_to_all_ds": True
    }

    try:
        qid = form_model.save()
    except DataObjectAlreadyExists as e:
        get_form_model_by_code(manager, "cli051").delete()
        qid = form_model.save()
    project1 = Project(name="Clinic Test Project", goals="This project is for automation", project_type="survey",
                       entity_type=CLINIC_ENTITY_TYPE[-1], devices=["sms", "web", "smartPhone"], activity_report='no',
                       sender_group="close")
    project1.qid = qid
    Reminder.objects.filter(project_id=project1.id).delete()

    project1.reminder_and_deadline = weekly_reminder_and_deadline

    try:
        project1.save(manager)
    except Exception:
        pass
    if (register_a_datasender):
        project1.data_senders.extend(["rep1"])
        project1.save(manager)

    return project1


def send_data_to_project_cli00_mp(manager):
    sms_player = SMSPlayerV2(manager, [])
    FROM_NUMBER = '1234567890'
    TO_NUMBER = '919880734937'
    transport = TransportInfo(SMS, FROM_NUMBER, TO_NUMBER)

    month = datetime.today().month
    year = datetime.today().year
    sms_player.add_survey_response(Request("cli00_mp cid001 %s.%s" % (month, year), transport))
    sms_player.add_survey_response(Request("cli00_mp cid001 %s.%s" % (month, year - 1), transport))
    sms_player.add_survey_response(Request("cli00_mp cid001 01.%s" % year, transport))
    sms_player.add_survey_response(Request("cli00_mp cid001 %s.%s" % (month, year), transport))

    tester_transport = TransportInfo(SMS, TEST_REPORTER_MOBILE_NUMBER, TO_NUMBER)
    sms_player.add_survey_response(Request("cli00_mp cid001 %s.%s" % (month, year), tester_transport))


def load_data():
    manager = load_manager_for_default_test_account()
    initializer.run(manager)
    CLINIC_ENTITY_TYPE = [u"clinic"]
    WATER_POINT_ENTITY_TYPE = [u"waterpoint"]
    PEOPLE_ENTITY_TYPE = [u"people"]
    create_entity_types(manager, [CLINIC_ENTITY_TYPE, WATER_POINT_ENTITY_TYPE, PEOPLE_ENTITY_TYPE])

    load_clinic_entities(CLINIC_ENTITY_TYPE, manager)
    load_waterpoint_entities(WATER_POINT_ENTITY_TYPE, manager)
    create_clinic_projects(CLINIC_ENTITY_TYPE, manager)
    create_project19(PEOPLE_ENTITY_TYPE, manager)
    #Register Reporters
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "1234567890"),
                                                              (NAME_FIELD, "Shweta")],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep1", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "261332592634"),
                                                              (NAME_FIELD, "David")],
             location=[u'Madagascar', u'Haute matsiatra', u'Ambohimahasoa', u'Camp Robin'],
             short_code="rep2", geometry={"type": "Point", "coordinates": [-20.9027586764, 47.165034158]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "1234567891"),
                                                              (NAME_FIELD, "Shilpa")],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep3", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "1234567892"),
                                                              (NAME_FIELD, "Asif")],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep4", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "919970059125"),
                                                              (NAME_FIELD, "Ritesh")],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep5", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "917798987116"),
                                                              (NAME_FIELD, "RiteshY")],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep6", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "917798987102"),
                                                              (NAME_FIELD, "AkshaY")],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep7", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "919049008976"),
                                                              (NAME_FIELD, "Ashwini")],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep8", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "2619876"),
                                                              (NAME_FIELD, "stefan")],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep10", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "2619875"),
                                                              (NAME_FIELD, "mamy")],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep11", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "1234123413"),
                                                              (NAME_FIELD, "Tester Pune")],
             location=[u'Bangalore', u'Karnatka', u'India', u'Asia'],
             short_code="rep276", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})
    register(manager, entity_type=REPORTER_ENTITY_TYPE, data=[(MOBILE_NUMBER_FIELD, "37287364782"),
                                                              (NAME_FIELD, "Datasender test")],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep13", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})

    load_sms_data_for_cli001(manager)
    load_web_data_for_cli001(manager)
    send_data_to_project_cli00_mp(manager)

    load_web_data_for_cli018(manager)
    load_sms_data_for_cli018(manager)

    create_trial_test_organization('chinatwu@gmail.com', 'COJ00000', False)
    create_trial_test_organization('chinatwu2@gmail.com', 'COJ00001', True)
    create_trial_test_organization('chinatwu3@gmail.com', 'COJ00002', False)
    create_trial_test_organization('chinatwu4@gmail.com', 'COJ00003', False)
    create_trial_test_organization('mamytest@mailinator.com', 'SLX364903', False)
    create_project_for_nigeria_test_orgnization()
    create_datasender_for_nigeria_test_organization()

    create_trial_test_organization('quotareached@mailinator.com', 'YDC120930', False)
    register_datasender_for_quota_reached_ngo()
    create_clinic3_project_for_quota_reached_ngo()
    create_questionnaire_templates()


def create_datasender_for_nigeria_test_organization():
    user = User.objects.get(username="samuel@mailinator.com")
    manager = get_database_manager(user)
    initializer.run(manager)
    register(manager, entity_type=REPORTER_ENTITY_TYPE,
             data=[(MOBILE_NUMBER_FIELD, "26112345"),
                   (NAME_FIELD, "Rasefo")],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep1", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})


def create_trial_test_organization(email, org_id, register_a_data_sender):
    manager = get_database_manager(User.objects.get(username=email))
    initializer.run(manager)
    CLINIC_ENTITY_TYPE = [u"clinic"]
    WATER_POINT_ENTITY_TYPE = [u"waterpoint"]
    create_entity_types(manager, [CLINIC_ENTITY_TYPE, WATER_POINT_ENTITY_TYPE])

    load_clinic_entities(CLINIC_ENTITY_TYPE, manager)
    load_waterpoint_entities(WATER_POINT_ENTITY_TYPE, manager)

    if (register_a_data_sender):
        register(manager, entity_type=REPORTER_ENTITY_TYPE,
                 data=[(MOBILE_NUMBER_FIELD, "1234567890"),
                       (NAME_FIELD, "Shweta")],
                 location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
                 short_code="rep1", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})

    create_clinic_project_for_trial_account(CLINIC_ENTITY_TYPE, manager, org_id, register_a_data_sender)
    return manager


def load_test_managers():
    return [get_database_manager(User.objects.get(username=email)) for email in TEST_EMAILS]


def load_all_managers():
    managers = []
    for org in OrganizationSetting.objects.all():
        manager = get_db_manager(org.document_store)
        managers.append(manager)
    return managers


def load_all_feed_managers():
    managers = []
    for org in OrganizationSetting.objects.all():
        manager = get_db_manager('feed_' + org.document_store)
        managers.append(manager)
    return managers


def load_test_feed_managers():
    return [get_feeds_database(User.objects.get(username=email)) for email in TEST_EMAILS]


def create_project_for_nigeria_test_orgnization():
    manager = get_database_manager(User.objects.get(username="gerard@mailinator.com"))
    initializer.run(manager)
    CLINIC_ENTITY_TYPE = [u"clinic"]
    create_entity_types(manager, [CLINIC_ENTITY_TYPE])

    questions = create_questions(CLINIC_ENTITY_TYPE)
    weekly_reminder_and_deadline = {
        "deadline_week": "5",
        "deadline_type": "Same",
        "has_deadline": True,
        "frequency_period": "week",
        "should_send_reminder_to_all_ds": True
    }
    create_project1(CLINIC_ENTITY_TYPE, manager, questions, weekly_reminder_and_deadline)


def register_datasender_for_quota_reached_ngo():
    manager = get_database_manager(User.objects.get(username="quotareached@mailinator.com"))
    register(manager, entity_type=REPORTER_ENTITY_TYPE,
             data=[(MOBILE_NUMBER_FIELD, "261123456"),
                   (NAME_FIELD, "Datasender Quota Reached")],
             location=[u'Madagascar', u'Menabe', u'Mahabo', u'Beronono'],
             short_code="rep1", geometry={"type": "Point", "coordinates": [-21.0399440737, 45.2363669927]})


def create_clinic3_project_for_quota_reached_ngo():
    manager = get_database_manager(User.objects.get(username="quotareached@mailinator.com"))
    questions = create_questions([u"clinic"])
    create_project3([u"clinic"], manager, questions)
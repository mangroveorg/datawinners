# vim: ai ts=4 sts=4 et sw= encoding=utf-8
from datetime import timedelta, date

from couchdb.mapping import  TextField, ListField, DictField
from django.db.models.fields import IntegerField, CharField, BooleanField
from django.db.models.fields.related import ForeignKey
from datawinners.accountmanagement.models import Organization
from datawinners.scheduler.deadline import Deadline, Month, Week
from mangrove.datastore.database import  DatabaseManager
from mangrove.datastore.documents import DocumentBase
from mangrove.errors.MangroveException import DataObjectAlreadyExists
from mangrove.form_model.form_model import FormModel
from mangrove.utils.types import  is_string
from django.db import models


class Reminder(models.Model):
    project_id = CharField(null=False, blank=False, max_length=264)
    day = IntegerField(null=True, blank=True)
    message = CharField(max_length=160)
    reminder_mode = CharField(null=False, blank=False, max_length=20, default='before_deadline')
    organization = ForeignKey(Organization)
    voided = BooleanField(default=False)

    def to_dict(self):
        return {'day': self.day, 'message': self.message, 'reminder_mode': self.reminder_mode}

    def void(self, void = True):
        self.voided = void
        self.save()

class ProjectState(object):
    INACTIVE = 'Inactive'
    ACTIVE = 'Active'
    TEST = 'Test'

class Project(DocumentBase):
    name = TextField()
    goals = TextField()
    project_type = TextField()
    entity_type = TextField()
    activity_report = TextField()
    devices = ListField(TextField())
    qid = TextField()
    state = TextField()
    sender_group = TextField()
    reminder_and_deadline = DictField()
    data_senders = ListField(TextField())
    reminders=ListField(DictField())

    def __init__(self, id=None, name=None, goals=None, project_type=None, entity_type=None, devices=None, state=ProjectState.INACTIVE, activity_report=None, sender_group=None, reminder_and_deadline=None):
        assert entity_type is None or is_string(entity_type), "Entity type %s should be a string." % (entity_type,)
        DocumentBase.__init__(self, id=id, document_type='Project')
        self.devices = []
        self.name = name.lower() if name is not None else None
        self.goals = goals
        self.project_type = project_type
        self.entity_type = entity_type
        self.devices = devices
        self.state = state
        self.activity_report = activity_report
        self.sender_group = sender_group
        self.reminder_and_deadline = reminder_and_deadline if reminder_and_deadline is not None else {}

    def deadline(self):
        return Deadline(self._frequency(), self._deadline_type())

    def _frequency(self):
        if self.reminder_and_deadline.get('frequency_period') == 'month':
            return Month(int(self.reminder_and_deadline.get('deadline_month')))
        if self.reminder_and_deadline.get('frequency_period') == 'week':
            return Week(int(self.reminder_and_deadline.get('deadline_week')))


    def has_deadline(self):
        if self.reminder_and_deadline.get('has_deadline') == 'True':
            return True
        return False
    
    def frequency_enabled(self):
        if self.reminder_and_deadline.get('frequency_enabled') == 'True':
            return True
        return False

    def reminders_enabled(self):
        if self.reminder_and_deadline.get('reminders_enabled') == 'True':
            return True
        return False

    def _deadline_type(self):
        if self.frequency_enabled():
            return self.reminder_and_deadline.get('deadline_type')

    def _frequency_period(self):
        return self.reminder_and_deadline.get('frequency_period')

    def get_deadline_day(self):
        if self.reminder_and_deadline.get('frequency_period') == 'month':
            return int(self.reminder_and_deadline.get('deadline_month'))

    def is_reminder_enabled(self):
        if self.reminder_and_deadline.get('reminders_enabled') == "True":
            return True

        return False

    def should_send_reminders(self, as_of):
        if self._deadline_type() == "Following":
            if self._frequency_period() == "week":
                as_of = as_of + timedelta(days=-7)
            if self._frequency_period() == "month":
                month = 12 if as_of.month == 1 else as_of.month - 1
                as_of = date(as_of.year, month, as_of.day)
        deadline = self.deadline()
        if as_of == deadline.next(as_of):
            return True
        return False

    def _check_if_project_name_unique(self, dbm):
        rows = dbm.load_all_rows_in_view('project_names', key=self.name)
        if len(rows) and rows[0]['value'] != self.id:
            raise DataObjectAlreadyExists('Project', "Name", "'%s'" % self.name)

    def save(self, dbm):
        assert isinstance(dbm, DatabaseManager)
        self._check_if_project_name_unique(dbm)
        return dbm._save_document(self)

    def update(self, value_dict):
        attribute_list = [item[0] for item in (self.items())]
        for key in value_dict:
            if key in attribute_list:
                setattr(self, key, value_dict.get(key).lower()) if key == 'name' else setattr(self, key,
                                                                                              value_dict.get(key))

    def update_questionnaire(self, dbm):
        form_model = dbm.get(self.qid, FormModel)
        form_model.name = self.name
        form_model.entity_type =  [self.entity_type] if is_string(self.entity_type) else self.entity_type
        form_model.save()

    def activate(self, dbm):
        form_model = dbm.get(self.qid, FormModel)
        form_model.activate()
        form_model.save()
        self.state = ProjectState.ACTIVE
        self.save(dbm)

    def deactivate(self, dbm):
        form_model = dbm.get(self.qid, FormModel)
        form_model.deactivate()
        form_model.save()
        self.state = ProjectState.INACTIVE
        self.save(dbm)

    def to_test_mode(self, dbm):
        form_model = dbm.get(self.qid, FormModel)
        form_model.set_test_mode()
        form_model.save()
        self.state = ProjectState.TEST
        self.save(dbm)

    def delete(self, dbm):
        dbm.database.delete(self)

    #The method name sucks but until we make Project DataObject we can't make the method name 'void'
    def set_void(self, dbm, void = True):
        self.void = void
        self.save(dbm)

def get_project(pid, dbm):
    return dbm._load_document(pid, Project)


def get_all_projects(dbm):
    return dbm.load_all_rows_in_view('all_projects')

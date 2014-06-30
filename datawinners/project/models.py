# vim: ai ts=4 sts=4 et sw= encoding=utf-8
from datetime import timedelta, date

from couchdb.mapping import TextField, ListField, DictField
from django.db.models.fields import IntegerField, CharField
from django.db.models.fields.related import ForeignKey
from django.db import models

from datawinners.accountmanagement.models import Organization
from datawinners.entity.data_sender import load_data_senders
from datawinners.scheduler.deadline import Deadline, Month, Week
from mangrove.datastore.database import DatabaseManager, DataObject
from mangrove.datastore.documents import DocumentBase, TZAwareDateTimeField, attributes, ProjectDocument
from mangrove.datastore.entity import Entity
from mangrove.errors.MangroveException import DataObjectAlreadyExists
from mangrove.form_model.form_model import FormModel, REPORTER
from mangrove.transport.repository.reporters import get_reporters_who_submitted_data_for_frequency_period
from mangrove.utils.types import is_string, is_empty


def get_all_reminder_logs_for_project(project_id, dbm):
    assert isinstance(dbm, DatabaseManager)
    rows = dbm.view.reminder_log(startkey=project_id, endkey=project_id, include_docs=True)
    return [ReminderLog.new_from_doc(dbm=dbm, doc=ReminderLog.__document_class__.wrap(row['doc'])) for row in rows]


class ReminderRepository(object):
    def get_all_reminders_for(self, organization_id):
        return Reminder.objects.filter(organization=organization_id)


def get_reminder_repository():
    return ReminderRepository()


class ReminderMode(object):
    BEFORE_DEADLINE = 'before_deadline'
    ON_DEADLINE = 'on_deadline'
    AFTER_DEADLINE = 'after_deadline'


class RemindTo(object):
    ALL_DATASENDERS = 'all_datasenders'
    DATASENDERS_WITHOUT_SUBMISSIONS = 'datasenders_without_submissions'


class Reminder(models.Model):
    project_id = CharField(null=False, blank=False, max_length=264)
    day = IntegerField(null=True, blank=True)
    message = CharField(max_length=160)
    reminder_mode = CharField(null=False, blank=False, max_length=20, default=ReminderMode.BEFORE_DEADLINE)
    organization = ForeignKey(Organization)

    def to_dict(self):
        return {'day': self.day, 'message': self.message, 'reminder_mode': self.reminder_mode, 'id': self.id}

    def void(self, void=True):
        self.voided = void
        self.save()

    def should_be_send_on(self, deadline, on_date):
        assert isinstance(on_date, date)
        deadline_date = self._get_applicapable_deadline_date(deadline, on_date)
        return on_date == deadline_date + timedelta(days=self._delta())

    def get_sender_list(self, project, on_date, dbm):
        if not project.reminder_and_deadline['should_send_reminder_to_all_ds']:
            deadline_date = self._get_applicapable_deadline_date(project.deadline(), on_date)
            return project.get_data_senders_without_submissions_for(deadline_date, dbm)
        return project.get_data_senders(dbm)

    def _delta(self):
        if self.reminder_mode == ReminderMode.ON_DEADLINE:
            return 0
        if self.reminder_mode == ReminderMode.BEFORE_DEADLINE:
            return -self.day
        if self.reminder_mode == ReminderMode.AFTER_DEADLINE:
            return self.day

    def _get_applicapable_deadline_date(self, deadline, on_date):
        if self.reminder_mode == ReminderMode.BEFORE_DEADLINE:
            return deadline.next_deadline(on_date)
        else:
            return deadline.current_deadline(on_date)

    def log(self, dbm, project_id, date, to_number, sent_status='sent', number_of_sms=0):
        log = ReminderLog(dbm=dbm, reminder=self, project_id=project_id, date=date, sent_status=sent_status,
                          number_of_sms=number_of_sms, to_number=to_number)
        log.save()
        return log


class ReminderLogDocument(DocumentBase):
    reminder_id = TextField()
    project_id = TextField()
    sent_status = TextField()
    number_of_sms = TextField()
    date = TZAwareDateTimeField()
    message = TextField()
    remind_to = TextField()
    reminder_mode = TextField()

    def __init__(self, id=None, reminder_id=None, project_id=None, sent_status=None, number_of_sms=None, date=None,
                 message=None, remind_to=None, reminder_mode=None):
        DocumentBase.__init__(self, id=id, document_type='ReminderLog')
        self.reminder_id = reminder_id
        self.project_id = project_id
        self.sent_status = sent_status
        self.number_of_sms = number_of_sms
        self.date = date
        self.message = message
        self.remind_to = remind_to
        self.reminder_mode = reminder_mode


class ReminderLog(DataObject):
    __document_class__ = ReminderLogDocument

    def __init__(self, dbm, reminder=None, sent_status=None, number_of_sms=None, date=None, project_id=None,
                 to_number=""):
        DataObject.__init__(self, dbm)
        if reminder is not None:
            if reminder.reminder_mode == ReminderMode.ON_DEADLINE:
                reminder_mode = self._format_string_before_saving(reminder.reminder_mode)
            else:
                reminder_mode = str(reminder.day) + ' days ' + self._format_string_before_saving(reminder.reminder_mode)
            doc = ReminderLogDocument(reminder_id=reminder.id, project_id=project_id, sent_status=sent_status,
                                      number_of_sms=number_of_sms, date=date, message=reminder.message,
                                      remind_to=self._format_string_before_saving(to_number),
                                      reminder_mode=reminder_mode)
            DataObject._set_document(self, doc)

    @property
    def reminder_mode(self):
        return self._doc.reminder_mode

    @property
    def remind_to(self):
        return self._doc.remind_to

    @property
    def message(self):
        return self._doc.message

    @property
    def date(self):
        return self._doc.date

    def _format_string_before_saving(self, value):
        return (' '.join(value.split('_'))).title()


class Project(FormModel):
    __document_class__ = ProjectDocument

    def _set_doc(self, form_code, is_registration_model, label, language, name):
        doc = ProjectDocument()
        doc.name = name
        doc.set_label(label)
        doc.form_code = form_code
        doc.active_languages = [language]
        doc.is_registration_model = is_registration_model
        DataObject._set_document(self, doc)

    def __init__(self, dbm, form_code=None, name=None, goals="", devices=None, sender_group=None,
                 language='en', fields=[]):
        FormModel.__init__(self, dbm=dbm, form_code=form_code, is_registration_model=False,
                           label="", language=language, name=name, fields=fields)
        if self._doc:
            self._doc.goals = goals
            self._doc.devices = devices
            self._doc.sender_group = sender_group
            self._doc.reminder_and_deadline = {"deadline_type": "Following",
                                               "should_send_reminder_to_all_ds": False,
                                               "has_deadline": True,
                                               "deadline_month": "5",
                                               "frequency_period": "month"}

    @classmethod
    def from_form_model(cls, form_model):
        return super(Project, cls).new_from_doc(form_model._dbm, ProjectDocument.wrap(form_model._doc._data))

    @property
    def data_senders(self):
        return self._doc.data_senders

    @property
    def goals(self):
        return self._doc.goals

    @data_senders.setter
    def data_senders(self, value):
        self._doc.data_senders = value

    @property
    def devices(self):
        return self._doc.devices

    @property
    def language(self):
        return self.activeLanguages[0]

    @property
    def is_outgoing_sms_replies_enabled(self):
        is_enabled = self._doc.is_outgoing_sms_replies_enabled
        return True if is_enabled is None else is_enabled

    @is_outgoing_sms_replies_enabled.setter
    def is_outgoing_sms_replies_enabled(self, enable_replies):
        self._doc.is_outgoing_sms_replies_enabled = enable_replies

    @property
    def reminder_and_deadline(self):
        return self._doc.reminder_and_deadline

    @reminder_and_deadline.setter
    def reminder_and_deadline(self, value):
        self._doc.reminder_and_deadline = value

    def get_data_senders(self, dbm):
        all_data, fields, label = load_data_senders(dbm, self.data_senders)
        return [dict(zip(fields, data["cols"])) for data in all_data]

    def get_associated_datasenders(self, dbm):
        keys = [([REPORTER], short_code) for short_code in self.data_senders]
        rows = dbm.view.by_short_codes(reduce=False, include_docs=True, keys=keys)
        return [Entity.new_from_doc(dbm, Entity.__document_class__.wrap(row.get('doc'))) for row in rows]

    def _get_data_senders_ids_who_made_submission_for(self, dbm, deadline_date):
        start_date, end_date = self.deadline().get_applicable_frequency_period_for(deadline_date)
        form_code = self.form_code
        data_senders_with_submission = get_reporters_who_submitted_data_for_frequency_period(dbm, form_code, start_date,
                                                                                             end_date)
        return [ds.short_code for ds in data_senders_with_submission]

    def get_data_senders_without_submissions_for(self, deadline_date, dbm):
        data_sender_ids_with_submission = self._get_data_senders_ids_who_made_submission_for(dbm, deadline_date)
        all_data_senders = self.get_data_senders(dbm)
        data_senders_without_submission = [data_sender for data_sender in all_data_senders if
                                           data_sender['short_code'] not in data_sender_ids_with_submission]
        return data_senders_without_submission

    def deadline(self):
        return Deadline(self._frequency(), self._deadline_type())

    def _frequency(self):
        if self.reminder_and_deadline.get('frequency_period') == 'month':
            return Month(int(self.reminder_and_deadline.get('deadline_month')))
        if self.reminder_and_deadline.get('frequency_period') == 'week':
            return Week(int(self.reminder_and_deadline.get('deadline_week')))

    def has_deadline(self):
        return self.reminder_and_deadline.get('has_deadline')

    def _deadline_type(self):
        return self.reminder_and_deadline.get('deadline_type')

    def _frequency_period(self):
        return self.reminder_and_deadline.get('frequency_period')

    def get_deadline_day(self):
        if self.reminder_and_deadline.get('frequency_period') == 'month':
            return int(self.reminder_and_deadline.get('deadline_month'))

    def should_send_reminders(self, as_of, days_relative_to_deadline):
        next_deadline_day = self.deadline().current(as_of)
        if next_deadline_day is not None:
            if as_of == next_deadline_day + timedelta(days=days_relative_to_deadline):
                return True
        return False

    def is_project_name_unique(self):
        rows = self._dbm.load_all_rows_in_view('project_names', key=self.name.lower())
        if len(rows) and rows[0]['value']["id"] != self.id:
            return False
        return True

    def _check_if_project_name_unique(self):
        if not self.is_project_name_unique():
            raise DataObjectAlreadyExists('Questionnaire', "Name", "'%s'" % self.name)

    def save(self, process_post_update=True):
        assert isinstance(self._dbm, DatabaseManager)
        self._check_if_project_name_unique()
        return super(Project, self).save()

    def update(self, value_dict):
        attribute_list = [item[0] for item in (self._doc.items())]
        for key in value_dict:
            if key in attribute_list:
                # if key == 'name':
                #     setattr(self._doc, key, value_dict.get(key))
                # else:
                    setattr(self._doc, key, value_dict.get(key))

    def set_void(self, void=True):
        self._doc.void = void

    def delete_datasender(self, dbm, entity_id):
        from datawinners.search.datasender_index import update_datasender_index_by_id

        self.data_senders.remove(entity_id)
        self.save(process_post_update=False)
        update_datasender_index_by_id(entity_id, dbm)

    def associate_data_sender_to_project(self, dbm, data_sender_code):
        if data_sender_code in self.data_senders: return
        from datawinners.search.datasender_index import update_datasender_index_by_id
        # Normally this case should not happen. However in a special case
        # blank id was sent from client side. So introduced this check.
        if data_sender_code:
            self.data_senders.append(data_sender_code)
            self.save(process_post_update=False)
            update_datasender_index_by_id(data_sender_code, dbm)


def get_all_projects(dbm, data_sender_id=None):
    if data_sender_id:
        rows = dbm.load_all_rows_in_view('projects_by_datasenders', startkey=data_sender_id, endkey=data_sender_id, include_docs=True)
        for row in rows:
            row.update({'value': row["doc"]})
        return rows
    return dbm.load_all_rows_in_view('all_projects')


def get_all_projects_for_datasender(dbm, data_sender_id):
    rows = dbm.load_all_rows_in_view('projects_by_datasenders', key=data_sender_id, include_docs=True)
    return rows


def get_all_project_names(dbm):
    return [{'name': result['value']["name"], 'id': result['value']["id"]} for result in dbm.load_all_rows_in_view("project_names")]


def count_projects(dbm, include_voided_projects=True):
    if include_voided_projects:
        rows = dbm.load_all_rows_in_view('count_projects', reduce=True, group_level=0)
    else:
        rows = dbm.load_all_rows_in_view('count_projects', reduce=True, group_level=1, key=False)

    return rows[0]['value'] if not is_empty(rows) else 0


def delete_datasenders_from_project(manager, data_sender_ids):
    for entity_id in data_sender_ids:
        associated_projects = get_all_projects(manager, data_sender_id=entity_id)
        for associated_project in associated_projects:
            project = Project.get(manager, associated_project['value']['_id'])
            project.delete_datasender(manager, entity_id)


def project_by_form_model_id(dbm, form_model_id):
    assert isinstance(dbm, DatabaseManager)
    assert is_string(form_model_id)
    rows = dbm.load_all_rows_in_view('project_by_form_model_id', key=form_model_id)
    if not len(rows):
        raise ProjectNotFoundException("project does not exist for form model id %s " % form_model_id)

    return Project._wrap_row(rows[0])


class ProjectNotFoundException(Exception):
    pass
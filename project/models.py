# vim: ai ts=4 sts=4 et sw= encoding=utf-8

from couchdb.mapping import  TextField, ListField
from mangrove.datastore.database import  DatabaseManager
from mangrove.datastore.documents import DocumentBase
from mangrove.errors.MangroveException import DataObjectAlreadyExists
from mangrove.form_model.form_model import FormModel
from mangrove.utils.types import  is_string



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

    def __init__(self, id=None, name=None, goals=None, project_type=None, entity_type=None, devices=None, state=ProjectState.INACTIVE, activity_report=None):
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

    def _check_if_project_name_unique(self, dbm):
        rows = dbm.load_all_rows_in_view('all_projects', key=self.name)
        if len(rows) and rows[0]['value']['_id'] != self.id:
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
        form_model.entity_type = self.entity_type
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

def get_project(pid, dbm):
    return dbm._load_document(pid, Project)


def get_all_projects(dbm):
    return dbm.load_all_rows_in_view('all_projects')

from couchdb.mapping import  TextField, ListField
from mangrove.datastore.database import get_db_manager, DatabaseManager
from mangrove.datastore.documents import DocumentBase

class Project(DocumentBase):
    name = TextField()
    goals = TextField()
    project_type = TextField()
    entity_type = TextField()
    devices = ListField(TextField())
    qid = TextField()

    def __init__(self, id=None, name=None, goals=None, project_type=None, entity_type=None, devices=None):
        DocumentBase.__init__(self, id=id, document_type='Project')
        self.name = name
        self.goals = goals
        self.project_type = project_type
        self.entity_type = entity_type
        self.devices = devices

    def save(self, dbm=None):
        if dbm is None:
            dbm = get_db_manager()
        assert isinstance(dbm, DatabaseManager)
        return dbm.save(self)
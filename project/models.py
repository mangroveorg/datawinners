from couchdb.mapping import  TextField, ListField
from mangrove.datastore.database import get_db_manager, DatabaseManager
from mangrove.datastore.documents import DocumentBase
from mangrove.utils.types import is_sequence

class Project(DocumentBase):
    name = TextField()
    goals = TextField()
    project_type = TextField()
    entity_type = TextField()
    devices = ListField(TextField())
    qid = TextField()

    def __init__(self, id=None, name=None, goals=None, project_type=None, entity_type=None, devices=[]):
        DocumentBase.__init__(self, id=id, document_type='Project')
        assert is_sequence(devices)
        self.devices=[]
        self.name = name
        self.goals = goals
        self.project_type = project_type
        self.entity_type = entity_type
        self.devices = devices
#        self.devices.append("web")

    def save(self, dbm=None):
        if dbm is None:
            dbm = get_db_manager()
        assert isinstance(dbm, DatabaseManager)
        return dbm.save(self).id

    def update(self,value_dict):
        attribute_list=[item[0] for item in (self.items())]
        for key in value_dict:
            if key in attribute_list:
                setattr(self,key,value_dict.get(key))


def get_project(pid,dbm=get_db_manager()):
    return dbm.load(pid,Project)


def get_all_projects(dbm=get_db_manager()):
    return dbm.load_all_rows_in_view('datawinners_views/' + 'all_projects')
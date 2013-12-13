#import requests
#
#
#_from = "919970059125"
#_to = "919880734937"
#
#
#for i in range(15,15):
#    message= "025 %s.21.2013 hello%s"%(i, i)
#    data = {"message": message, "from_msisdn": _from, "to_msisdn": _to}
#    resp = requests.post("http://localhost:8000/submission", data)
#    print resp.text
#
##for i in range(1,3):
##    message= "001 %s.11.21013"%i
##    data = {"message": message, "from_msisdn": _from, "to_msisdn": _to}
##    resp = requests.post("http://localhost:8000/submission", data)
##    print resp.text
from datawinners.main.database import get_db_manager
from mangrove.datastore.entity import _from_row_to_entity


def get_all_deleted_entities(dbm, entity_type):
    rows = dbm.view.entity_by_short_code(key=[entity_type,'act'], reduce=False, include_docs=True)
    return [_from_row_to_entity(dbm, row) for row in rows]

dbm = get_db_manager('hni_testorg_slx364903')
print get_all_deleted_entities(dbm,['fokontany'])
import uuid
from django.test import Client

_from = "1234123413"
_to = "919880734937"

client = Client()
client.login(username='tester150411@gmail.com', password='tester150411')
#for i in range(1, 31):
#    message = "fir answer%s answer%s answer%s 3,3 56789%s" %(i,i,i,i)
#    data = {"message": message, "from_msisdn": _from, "to_msisdn": _to, "message_id": uuid.uuid1().hex}
#    resp = client.post("/submission", data)
#    print resp.content
for i in range(1, 40):
    message = "001 fir3"
    data = {"message": message, "from_msisdn": "2619875", "to_msisdn": _to, "message_id": uuid.uuid1().hex}
    resp = client.post("/submission", data)
    print resp.content

#for i in range(1,3):
#    message= "001 %s.11.21013"%i
#    data = {"message": message, "from_msisdn": _from, "to_msisdn": _to}
#    resp = requests.post("http://localhost:8000/submission", data)
#    print resp.text
#from datawinners.main.database import get_db_manager
#from mangrove.datastore.entity import _from_row_to_entity


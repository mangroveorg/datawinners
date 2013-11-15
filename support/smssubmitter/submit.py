import requests


_from = "917798987116"
_to = "919880734937"

#
# for i in range(1,31):
#     message= "001 %s.11.2013"%i
#     data = {"message": message, "from_msisdn": _from, "to_msisdn": _to}
#     resp = requests.post("http://localhost:8000/submission", data)
#     print resp.text

for i in range(1, 30):
    message = "cli001 cid001 name%s %d 2.2.2012 a a 2,2 a" % (i,i)
    data = {"message": message, "from_msisdn": _from, "to_msisdn": _to}
    resp = requests.post("http://localhost:8000/submission", data)
    print resp.text
import requests


_from = "2342342341"
_to = "234234234212"


for i in range(1,31):
    message= "001 %s.11.2013"%i
    data = {"message": message, "from_msisdn": _from, "to_msisdn": _to}
    resp = requests.post("http://localhost:8000/submission", data)
    print resp.text

for i in range(1,3):
    message= "001 %s.11.21013"%i
    data = {"message": message, "from_msisdn": _from, "to_msisdn": _to}
    resp = requests.post("http://localhost:8000/submission", data)
    print resp.text
import uuid
from django.test import Client
import json
import random


_from = "1234123413"
_to = "919880734937"


def project_name(code):
    return "Survey %s" % code


def random_string(length=6):
    return ''.join(random.sample('abcdefghijklmnopqrs', length))


target_qnaire_vs_questions = [(50, 10000), (50, 25000), (50, 50000), (50, 100000),
                              (100, 10000), (100, 25000), (100, 50000), (100, 100000),
                              (150, 10000), (150, 25000), (150, 50000), (150, 100000),
                              (200, 10000), (200, 25000), (200, 50000), (200, 100000),
                              (250, 10000), (250, 25000), (250, 50000), (250, 100000),
                              (300, 10000), (300, 25000), (300, 50000),
                              (350, 10000), (350, 25000), (350, 50000),
                              (400, 10000), (400, 15000), (400, 20000),
                              (450, 10000), (450, 15000),
                              (500, 10000)]

qnaire_vs_questions = [(100, 10000), (150, 10000), (200, 10000), (250, 10000), (300, 10000), (350, 10000), (400, 10000),
                       (450, 10000), (500, 10000)]
try:

    question = {"title": "When did you donate", "code": "q3", "type": "date", 'date_format': "dd.mm.yyyy",
                "instruction": "Enter a date"}
    client = Client()
    client.login(username='tester150411@gmail.com', password='tester150411')

    for q_count, s_count in qnaire_vs_questions:
        print q_count.__str__() + "asdasdasd" + s_count.__str__()
        questions = []
        for i in range(q_count):
            q = question.copy()
            q['code'] = "q" + i.__str__()
            q['title'] = random_string(13)
            questions.append(q)
        questionnaire_code = q_count + s_count
        client.post('/project/wizard/create/',
                    {'profile_form': '{"name":"%s","language":"en"}' % project_name(questionnaire_code),
                     'question-set': '%s' % json.dumps(questions),
                     'questionnaire-code': questionnaire_code
                    })
        for i in range(1, s_count):
            message = questionnaire_code.__str__()
            for i in range(q_count):
                message += " 25.12.2011"
            data = {"message": message, "from_msisdn": _from, "to_msisdn": _to, "message_id": uuid.uuid1().hex}
            resp = client.post("/submission", data)

except Exception as e:
    print e.message
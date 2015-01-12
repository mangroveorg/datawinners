import json
import os
import re
import random

from django.test import Client
from migration.couch.utils import migrate, DWThreadPool


_from = "1234123413"
_to = "919880734937"


def random_string(length=6):
    return ''.join(random.sample('abcdefghijklmnopqrs', length))


qnaire_vs_questions = [(10, 2000)]


def make_submission():
    print "enter"
    submission_data = open(os.path.join(current_diretory, "imag_project_data/submission_data_image.xml"), 'r').read()
    submission_data = re.sub("tmpdt7nQf", project_name, submission_data)
    submission_data = re.sub("<form_code>053", "<form_code>" + questionnaire_code, submission_data)
    client.post(path='/xlsform/web_submission/',
                data={'form_data': submission_data, 'form_code': questionnaire_code,
                      'locate.png': open(os.path.join(current_diretory, 'imag_project_data/locate.png'), 'rb')})
    print "exit"


try:

    client = Client()
    client.login(username='tester150411@gmail.com', password='tester150411')

    for q_count, s_count in qnaire_vs_questions:
        questionnaire_code = q_count + s_count
        project_name = random_string(13)
        current_diretory = os.path.dirname(__file__)
        response = json.loads(client.post(
            path='/xlsform/upload/?pname=' + project_name + '&qqfile=image.xlsx',
            data=open(os.path.join(current_diretory, 'imag_project_data/image.xlsx'), 'r').read(),
            content_type='application/octet-stream').content)
        questionnaire_code = response['form_code']
        project_id = response.get('project_id')
        pool = DWThreadPool(3, 3)
        for i in range(0, s_count):
            pool.submit(make_submission)
        pool.wait_for_completion()

except Exception as e:
    print e.message
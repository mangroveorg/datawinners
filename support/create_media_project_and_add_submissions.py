import json
import os
import re
import random

from django.test import Client
from migration.couch.utils import migrate, DWThreadPool


_from = "1234123413"
_to = "919880734937"


def random_string(length=6):
    return ''.join(random.sample('abcdefghijklmnopqrstuvwxyxz', length))


qnaire_vs_questions = [(10, 100), (10, 100)]


def make_submission(media):
    print "enter"
    submission_data = open(os.path.join(current_diretory, "imag_project_data/submission_data.xml"), 'r').read()
    submission_data = re.sub("tmpdt7nQf", project_name, submission_data)
    submission_data = re.sub("locate.png", media[1], submission_data)
    submission_data = re.sub("<form_code>053", "<form_code>" + questionnaire_code, submission_data)
    client.post(path='/xlsform/web_submission/',
                data={'form_data': submission_data, 'form_code': questionnaire_code,
                      media[1]: open(os.path.join(current_diretory, 'imag_project_data/'+media[1]), 'rb')})
    print "exit"

def _get_media():
    media = [('image', 'image.png'), ('video', 'video.mp4')]
    for med in media:
        yield med
try:

    client = Client()
    client.login(username='sairama@thoughtworks.com', password='ramya1234')
    media = _get_media()

    for q_count, s_count in qnaire_vs_questions:
        next_media = next(media)
        questionnaire_code = q_count + s_count
        project_name = random_string(13)
        current_diretory = os.path.dirname(__file__)
        response = json.loads(client.post(
            path='/xlsform/upload/?pname=' + project_name + '&qqfile='+next_media[0]+'.xlsx',
            data=open(os.path.join(current_diretory, 'imag_project_data/'+next_media[0]+'.xlsx'), 'r').read(),
            content_type='application/octet-stream').content)
        questionnaire_code = response['form_code']
        project_id = response.get('project_id')
        pool = DWThreadPool(3, 3)
        for i in range(0, s_count):
            pool.submit(make_submission, next_media)
        pool.wait_for_completion()

except Exception as e:
    print e.message
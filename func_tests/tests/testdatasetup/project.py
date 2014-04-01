import json
from framework.utils.common_utils import random_string


def create_multi_choice_project(client, questionnaire_code=random_string()):
    project_create_response = json.loads(client.post('/project/wizard/create/', {'profile_form': '{"name":"Blood Group Survey %s","language":"en"}' % questionnaire_code,
                                                            'question-set': '[{"title":"Blood Group","code":"code","type":"select1","choices":[{"value":{"text":"A","val":"a"}},{"value":{"text":"B","val":"b"}},{"value":{"text":"AB","val":"c"}},{"value":{"text":"O","val":"d"}}]}]',
                                                            'questionnaire-code': questionnaire_code
        }).content)
    assert project_create_response["success"]
    return project_create_response["project_id"]
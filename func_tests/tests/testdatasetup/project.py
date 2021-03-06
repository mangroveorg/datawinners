import json
from framework.utils.common_utils import random_string


def blood_test_project_name(code = random_string()):
    return "Blood Group Survey %s"%code

blood_group_question_json = {"title":"Blood Group","code":"q2","type":"select1","choices":[{"value":{"text":"A","val":"a"}},{"value":{"text":"B","val":"b"}},{"value":{"text":"AB","val":"c"}},{"value":{"text":"O","val":"d"}}], "instruction":"Choose 1 answer from the list. Example: a"}
date_question1_json = {"title":"When did you donate","code":"q3","type":"date",'date_format': "dd.mm.yyyy", "instruction":"Enter a date"}
date_question2_json = {"title":"When did you donate next","code":"q4","type":"date",'date_format': "mm.yyyy", "instruction":"Enter a date"}
clinic_unique_id_question = {"title":"Clinic","code":"q2","type":"unique_id","uniqueIdType":"clinic","required":True,"display":"test","instruction":"Answer must be 20 characters maximum"}
second_clinic_uid_question = {"title":"Clinic1","code":"q5","type":"unique_id","uniqueIdType":"clinic","required":True,"display":"test1","instruction":"Answer must be 20 characters maximum"}
people_unique_id_question = {"uniqueIdType":"people", "title": "patient", "code": "code", "type": "unique_id", "required": True, "display": "patient", "instruction": "Answer must be 20 characters maximum"}
waterpoint_unique_id_question = {"uniqueIdType":"waterpoint", "title": "waterpoint", "code": "q6", "type": "unique_id", "required": True, "display": "waterpoint", "instruction": "Answer must be 20 characters maximum"}

def create_multi_choice_project(client, questionnaire_code=random_string()):
    return create_project(client, questionnaire_code, [blood_group_question_json, date_question1_json, date_question2_json])

def create_unique_id_project(client, questionnaire_code=random_string()):
    return create_project(client, questionnaire_code, [clinic_unique_id_question])

def create_multiple_unique_id_project(client, questionnaire_code=random_string()):
    return create_project(client, questionnaire_code, [people_unique_id_question, clinic_unique_id_question])

def create_project_with_multiple_unique_id_of_same_type(client, questionnaire_code=random_string()):
    #Project with multiple same unique id questions.
    return create_project(client, questionnaire_code, [clinic_unique_id_question, second_clinic_uid_question, waterpoint_unique_id_question])


def create_project(client, questionnaire_code, questions):
    json_response = client.post('/project/wizard/create/', {'profile_form': '{"name":"%s","language":"en"}' % blood_test_project_name(questionnaire_code),
                                                            'question-set': '%s' % json.dumps(questions),
                                                            'questionnaire-code': questionnaire_code
        }).content
    project_create_response = json.loads(json_response)
    assert project_create_response["success"]
    return project_create_response["project_id"]
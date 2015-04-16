import json
from framework.utils.common_utils import random_number


def create_questionnaire(client):
    questionnaire_name = "Questionnaire" + random_number(3)
    questionnaire_code = random_number(3)
    questionnaire_data = {
        'is_open_survey': ['true'],
        'profile_form': ['{"name":"' + questionnaire_name + '"}'],
        u'questionnaire-code': [str(questionnaire_code)],
        u'question-set': [u'['
                          u'{"options":{"name":"",'
                          u'"code":"code",'
                          u'"required":true,'
                          u'"language":"en",'
                          u'"choices":[],'
                          u'"length_limiter":'
                          u'"length_unlimited","length":{"min":1,"max":""},'
                          u'"range":{"min":"","max":""},'
                          u'"label":"",'
                          u'"date_format":"mm.yyyy",'
                          u'"instruction":"Answer must be a text",'
                          u'"newly_added_question":false,'
                          u'"event_time_field_flag":false,"unique_id_type":null},'
                          u'"newly_added_question":true,"range_min":"",'
                          u'"event_time_field_flag":false,'
                          u'"range_max":"",'
                          u'"min_length":1,'
                          u'"max_length":"",'
                          u'"name":"",'
                          u'"title":"Q1",'
                          u'"code":"code",'
                          u'"type":"text",'
                          u'"isEntityQuestion":false,'
                          u'"uniqueIdType":null,'
                          u'"showDateFormats":false,'
                          u'"showAddRange":false,'
                          u'"showAddTextLength":true,'
                          u'"required":true,'
                          u'"answerType":"text",'
                          u'"display":"Q1",'
                          u'"choices":[{"value":{"text":"default","val":"a"},"valid":true,"error":""}],'
                          u'"choiceCanBeDeleted":false,"showUniqueId":false,"date_format":"mm.yyyy","length_limiter":"length_unlimited",'
                          u'"showLengthLimiter":false,'
                          u'"instruction":"Answer must be a word",'
                          u'"isAChoiceTypeQuestion":"none"}]']}

    response_created_questionnaire = client.post(path='/project/wizard/create/',
                                                      data=questionnaire_data)

    response_dict = json.loads(response_created_questionnaire.content)
    project_id = response_dict['project_id']

    return project_id
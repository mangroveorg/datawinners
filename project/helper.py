import re
from mangrove.datastore.question import TextQuestion

def create_question_list(post_dict):
    keys = post_dict.keys()
    max_index = _get_max_index(keys)
    questions = make_list(post_dict,max_index)
    return questions

def _get_max_index(keys):
    m = max(map(lambda x : _get_index(x), keys))
    return m

def _get_index(str):
    regex = re.compile(r".+?\[(?P<G1>\d+)\]")
    d = regex.match(str)
    if d:
        return int(d.group('G1'))
    return 0

def make_list(post_dict,max_index):
    question_list=[]
    for i in range(max_index + 1):
#        current_question={'question-title':None,'question-code':None}#create a list of all present values with None where not present
        current_question={}
        for key in current_question:
                current_question[key]=post_dict.get(key + '[' + str(i) + ']')
        question_list.append(current_question.copy())
    return question_list

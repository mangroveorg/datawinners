from mangrove.datastore.field import TextField, IntegerField, SelectField
from mangrove.datastore.form_model import FormModel

def create_question(post_dict):
    if post_dict["type"]=="text":
        return TextField(post_dict["title"],post_dict["code"],post_dict["description"])
    if post_dict["type"]=="integer":
        return IntegerField(post_dict["title"],post_dict["code"],post_dict["description"])
    if post_dict["type"]=="choice":
        options = [choice["value"] for choice in post_dict["choices"]]
        return SelectField(post_dict["title"],post_dict["code"],post_dict["description"],options)


def create_questionnaire(post,dbm):
    question_list=[]
    for each in post:
        question_list.append(create_question(each))
    return FormModel(dbm, entity_type_id="SomeType", name="SomeName", label="Some model",
                                    form_code="1", type='Sometype', fields=question_list)

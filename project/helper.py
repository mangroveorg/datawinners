# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mangrove.datastore.database import get_db_manager

from mangrove.datastore.field import TextField, IntegerField, SelectField
from mangrove.datastore.form_model import FormModel, get

def create_question(post_dict):
    if post_dict["type"]=="text":
        return TextField(post_dict["title"],post_dict["code"],post_dict["description"])
    if post_dict["type"]=="integer":
        return IntegerField(post_dict["title"],post_dict["code"],post_dict["description"])
    if post_dict["type"]=="choice":
        options = [choice["value"] for choice in post_dict["choices"]]
        return SelectField(post_dict["title"],post_dict["code"],post_dict["description"],options)


def create_questionnaire(post,dbm=get_db_manager()):
    entity_id_question = TextField(name="What are you reporting on?", question_code="eid", label="Entity being reported on",entity_question_flag=True)
    return FormModel(dbm, entity_type_id=post["entity_type"], name=post["name"], label="Some model",
                                    form_code=post["questionnaire_code"], type=post["questionnaire_type"], fields=[entity_id_question])


def load_questionnaire(questionnaire_id):
    return get(get_db_manager(), questionnaire_id)


def save_questionnaire(form_model,post_dictionary):
    entity_id_question = TextField(name="What are you reporting on?", question_code="eid", label="Entity being reported on",entity_question_flag=True)
    form_model.delete_all_questions()
    for question in post_dictionary:
        form_model.add_question(create_question(question))
    form_model.add_question(entity_id_question)
    return form_model
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mangrove.datastore.database import get_db_manager

from mangrove.datastore.field import TextField, IntegerField, SelectField
from mangrove.form_model.form_model import FormModel, get

def create_question(post_dict):
    if post_dict["type"]=="text":
        return TextField(name=post_dict["title"],question_code=post_dict["code"],label=post_dict["description"],entity_question_flag=post_dict["is_entity_question"])
    if post_dict["type"]=="integer":
        range = {"min":post_dict["range_min"], "max":post_dict["range_max"]}
        return IntegerField(post_dict["title"],post_dict["code"],post_dict["description"], range)
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
    form_model.delete_all_fields()
    for question in post_dictionary:
        form_model.add_field(create_question(question))
    return form_model
import sys

from datawinners.entity.helper import question_code_generator
from datawinners.main.database import get_db_manager
from datawinners.search import entity_form_model_change_handler
from datawinners.utils import random_string
from mangrove.datastore.entity_type import define_type
from mangrove.form_model.field import TextField, ShortCodeField
from mangrove.form_model.form_model import SHORT_CODE_FIELD, EntityFormModel, NAME_FIELD


def create_identification_number_type(db_name, entity_type, no_of_questions):
    dbm = get_db_manager(db_name)
    define_type(dbm, [entity_type])
    form_model = _create_registration_form(dbm, entity_type, no_of_questions)
    form_model.save()
    entity_form_model_change_handler(form_model._doc, dbm)


def _create_registration_form(manager, entity_name, no_of_questions):
    entity_type = [entity_name]
    code_generator = question_code_generator()
    form_code = random_string()
    questions = []
    for a in range(no_of_questions - 2):
        code = code_generator.next()
        question = TextField(name=code, code=code,
                             label=random_string(15),
                             defaultValue="some default value",
                             instruction="Enter a %(entity_type)s first name" % {'entity_type': entity_name})
        questions.append(question)

    question = TextField(name=NAME_FIELD, code=code_generator.next(),
                             label=random_string(15),
                             defaultValue="some default value",
                             instruction="Enter a %(entity_type)s first name" % {'entity_type': entity_name})
    questions.append(question)

    question = ShortCodeField(name=SHORT_CODE_FIELD, code=code_generator.next(),
                              label="What is the %(entity_type)s's Unique ID Number?" % {
                                  'entity_type': entity_name},
                              defaultValue="some default value",
                              instruction=unicode("Enter an id, or allow us to generate it"), required=False)
    questions.append(question)

    form_model = EntityFormModel(manager, name=entity_name, form_code=form_code, fields=questions,
                                 is_registration_model=True,
                                 entity_type=entity_type)
    return form_model


if __name__ == "__main__":
    args = sys.argv
    entity_type = args[1] if len(args) > 1 else random_string(3)
    no_of_questions = args[2] if len(args) > 2 else 6
    create_identification_number_type('hni_testorg_slx364903', entity_type, no_of_questions)
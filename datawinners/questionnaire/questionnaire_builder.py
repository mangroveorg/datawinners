from mangrove.form_model.field_builder import QuestionBuilder
from mangrove.form_model.form_model import EntityFormModel
from mangrove.form_model.validators import UniqueIdExistsValidator
from datawinners.entity.helper import question_code_generator


class QuestionnaireBuilder(object):
    def __init__(self, form_model, dbm, question_builder=None):
        if question_builder is None: question_builder = QuestionBuilder()
        self.form_model = form_model
        self.question_builder = question_builder
        self.question_code_generator = question_code_generator()

    def _generate_fields_by_question_set(self, max_code, question_set):
        new_fields = []

        for question in question_set:
            question_code = question['code']

            if not self.form_model.xform and question_code == 'code':
                max_code += 1
                question_code = 'q%s' % max_code

            field = self.question_builder.create_question(question, question_code)
            new_fields.append(field)
        return new_fields

    def _update_unique_id_validator(self):
        if not isinstance(self.form_model, EntityFormModel):
            if self.form_model.entity_questions:
                self.form_model.add_validator(UniqueIdExistsValidator)
            else:
                self.form_model.remove_validator(UniqueIdExistsValidator)

    def update_questionnaire_with_questions(self, question_set):
        origin_json_fields = [f._to_json() for f in self.form_model.fields]
        max_code = None
        if not self.form_model.xform:
            max_code = get_max_code_in_question_set(origin_json_fields or question_set)
        new_fields = self._generate_fields_by_question_set(max_code, question_set)
        self.form_model.create_snapshot()
        self.form_model.delete_all_fields()
        [self.form_model.add_field(each) for each in new_fields]
        self._update_unique_id_validator()
        return self

    def update_reminder(self, reminder_and_deadline):
        if reminder_and_deadline:
            self.form_model.reminder_and_deadline = reminder_and_deadline
        return self

    def update_outgoing_sms_enabled_flag(self, is_outgoing_sms_enabled):
        self.form_model.is_outgoing_sms_replies_enabled = is_outgoing_sms_enabled == 'true'


def get_max_code(fields):
    json_fields = [f._to_json() for f in fields]
    return get_max_code_in_question_set(json_fields)


def get_max_code_in_question_set(question_set):
    codes = [int(q['code'][1:]) for q in question_set if q['code'].startswith('q')]
    return max(codes) if codes else 1

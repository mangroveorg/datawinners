from mangrove.form_model.form_model import EntityFormModel

class ResponseBuilder(object):
    def __init__(self, form_model, processed_data):
        self.form_model = form_model
        self.processed_data = processed_data

    def get_expanded_response(self):
        new_dict = self.form_model.stringify(self.processed_data)
        if isinstance(self.form_model, EntityFormModel):
            name_code = self.form_model.get_entity_name_question_code()
            short_code_code = self.form_model.entity_questions[0].code
            return "%s (%s)" % (self.processed_data.get(name_code), self.processed_data.get(short_code_code))

        return "; ".join([each for each in new_dict.values()])

    def get_response_for_sms_subject_registration(self):
        name_code = self.form_model.get_entity_name_question_code()
        short_code_code = self.form_model.entity_questions[0].code
        entity_type = self.form_model.entity_type
        return [entity_type[0],self.processed_data.get(name_code),
                self.processed_data.get(short_code_code)]



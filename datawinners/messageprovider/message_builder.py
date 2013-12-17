class ResponseBuilder(object):
    def __init__(self, form_model, processed_data):
        self.form_model = form_model
        self.processed_data = processed_data

    def get_expanded_response(self):
        new_dict = self.form_model.stringify(self.processed_data)
        if self.form_model.is_entity_type_reporter():
            new_dict.pop(self.form_model.entity_question.code)
        return "; ".join([each for each in new_dict.values()])

    def get_expanded_response_with_ordered_question_code(self):
        new_dict = self.form_model.stringify(self.processed_data)
        if self.form_model.is_entity_type_reporter():
            return self._get_response_for_entity_defaults_to_reporter(new_dict)
        else:
            response = " ".join([": ".join(["q%s" % str(index+1), each]) for index, each in enumerate(new_dict.values())])
            return response

    def _get_response_for_entity_defaults_to_reporter(self, new_dict):
        response = " ".join([": ".join(["q%s" % str(index), each]) for index, each in enumerate(new_dict.values()) if index != 0])
        response = "%s: %s %s" % (new_dict.keys()[0], new_dict.values()[0], response)
        return response.strip()
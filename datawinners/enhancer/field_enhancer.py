from mangrove.form_model.field import SelectField
import re

def enhance():
    def _get_value_by_option(self, option):
        return [opt['text'][self.language] for opt in self.options if opt['val'] == option][0]

    SelectField.get_value_by_option = _get_value_by_option

    def _get_option_value_list(field, question_value):
        if question_value is None: return []

        options = re.findall(r'[1-9]?[a-z]', question_value)
        return [field.get_value_by_option(option) for option in options ]

    SelectField.get_option_value_list = _get_option_value_list
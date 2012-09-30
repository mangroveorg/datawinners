from mangrove.form_model.field import SelectField
import re

NOT_AVAILABLE = "N/A"

def enhance():
    def _get_value_by_option(self, option):
        for opt in self.options:
            opt_text = opt['text']
            opt_value = opt['val']
            if opt_value.lower() == option.lower():
                if opt_text.has_key(self.language) :
                    return opt_text[self.language]
                elif opt_value.lower() == option.lower():
                    return opt_text[opt_text.keys()[0]]
        return NOT_AVAILABLE

    SelectField.get_value_by_option = _get_value_by_option

    def _get_option_value_list(field, question_value):
        if question_value is None: return []

        options = re.findall(r'[1-9]?[a-zA-Z]', question_value)
        return [field.get_value_by_option(option) for option in options ]

    SelectField.get_option_value_list = _get_option_value_list

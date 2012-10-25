from mangrove.form_model.field import SelectField
import re

NOT_AVAILABLE = "N/A"

def enhance():
    def _get_value_by_option(self, option):
        for opt in self.options:
            opt_text = opt['text']
            opt_value = opt['val']
            if opt_value.lower() == option.lower():
                if opt_text.has_key('en') :
                    return opt_text['en']
                elif opt_value.lower() == option.lower():
                    return opt_text[opt_text.keys()[0]]
        return None

    SelectField.get_value_by_option = _get_value_by_option

    def _get_option_value_list(field, question_value):
        if question_value is None: return []

        options = re.findall(r'[1-9]?[a-zA-Z]', question_value)
        result = []
        for option in options:
            option_value = field.get_value_by_option(option)
            if option_value:
                result.append(option_value)
        return result

    SelectField.get_option_value_list = _get_option_value_list

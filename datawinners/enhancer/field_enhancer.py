from mangrove.form_model.field import SelectField

def get_value_by_option(self, option):
    return [opt['text'][self.language] for opt in self.options if opt['val'] == option][0]

SelectField.get_value_by_option = get_value_by_option

def enhance():pass
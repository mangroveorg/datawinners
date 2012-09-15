from mangrove.form_model.form_model import FormModel

def non_rp_fields(self):
    return [field for field in self.fields if not field.is_event_time_field]

def has_report_period_question(self):
    return len(filter(lambda x: x.is_event_time_field , self.fields)) > 0

FormModel.non_rp_fields = non_rp_fields
FormModel.has_report_period_question = has_report_period_question

def enhance():pass

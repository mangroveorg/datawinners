from mangrove.form_model.form_model import FormModel

def enhance():
    def non_rp_fields(self):
        return [field for field in self.fields if not field.is_event_time_field]

    FormModel.non_rp_fields = non_rp_fields


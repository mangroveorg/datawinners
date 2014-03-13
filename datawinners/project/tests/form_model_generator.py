# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mock import Mock
from mangrove.form_model.field import TextField, SelectField, DateField, GeoCodeField, UniqueIdField
from mangrove.form_model.form_model import FormModel

class FormModelGenerator(object):
    def __init__(self, database_manager):
        self.database_manager = database_manager
        self.init_form_model_fields()

    def form_model(self, form_code="cli002"):
        return FormModel(self.database_manager, name="AIDS", label="Aids form_model", form_code=form_code, type='survey',
            fields=[self.eid_field, self.rp_field, self.symptoms_field, self.blood_type_field],
            entity_type=["clinic"])

    def subject_form_model_without_rp(self):
        return FormModel(self.database_manager, name="AIDS", label="Aids form_model", form_code="cli002", type='survey',
            fields=[self.eid_field, self.symptoms_field, self.blood_type_field], entity_type=["clinic"])

    def summary_form_model_without_rp(self):
        return FormModel(self.database_manager, name="AIDS", label="Aids form_model", form_code="cli002", type='survey',
            fields=[self.eid_field, self.symptoms_field, self.blood_type_field],
            entity_type=["reporter"])

    def summary_form_model_with_rp(self):
        return FormModel(self.database_manager, name="AIDS", label="Aids form_model", form_code="cli002", type='survey',
            fields=[self.rp_field, self.eid_field, self.symptoms_field, self.blood_type_field],
            entity_type=["reporter"])

    def form_model_with_gps_question(self):
        return FormModel(self.database_manager, name="AIDS", label="Aids form_model", form_code="cli002", type='survey',
            fields=[self.eid_field, self.gps_field], entity_type=["clinic"])

    def init_form_model_fields(self):
        self.eid_field = UniqueIdField(unique_id_type='clinic',label="What is associated entity?", code="EID", name="What is associatéd entity?")
        self.rp_field = DateField(label="Report date", code="RD", name="What is réporting date?",
            date_format="dd.mm.yyyy", event_time_field_flag=True,
            instruction="Answer must be a date in the following format: day.month.year. Example: 25.12.2011")
        self.symptoms_field = SelectField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?",
            options=[("Rapid weight loss", "a"), ("Dry cough", "2b"), ("Pneumonia", "c"),
                     ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False)
        self.blood_type_field = SelectField(label="What is your blood group?", code="BG",
            name="What is your blood group?",
            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True)
        self.gps_field = GeoCodeField(name="field1_Loc", code="gps", label="Where do you stay?")


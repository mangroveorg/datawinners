# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.forms.fields import CharField, ChoiceField, MultipleChoiceField
from django.forms.forms import Form
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.entity import load_all_entity_types
from django import forms

class ProjectProfile(Form):
    PROJECT_TYPE_CHOICES = (('survey','Survey project: I want to collect data from the field'),('public information','Public information: I want to send information'))
    DEVICE_CHOICES = (('sms','SMS'),('smartphone','Smart Phone'))
    name=CharField(required=True)
    goals = CharField(max_length=300,label='Project Background And Goals',required=False)
    project_type = ChoiceField(label='Project Type',required=True,widget=forms.RadioSelect,choices=PROJECT_TYPE_CHOICES)
    entity_type=ChoiceField(label="Subjects", required=True)
    device = MultipleChoiceField(label='Device',widget=forms.CheckboxSelectMultiple,choices=DEVICE_CHOICES,required=True)
        
#    questionnaire_type=CharField(required=True)
#    questionnaire_code = CharField(label="Questionnaire Code",required=True)


    def get_entity_types(self):
            manager = get_db_manager()
            type_dict = load_all_entity_types(manager)
            type_list = [(k, v) for k, v in type_dict.items()]
            return type_list

    def __init__(self, *args, **kwargs):
        super(ProjectProfile, self).__init__(*args, **kwargs)
        type_list = self.get_entity_types()
        self.fields['entity_type']._set_choices(type_list)

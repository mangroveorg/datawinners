# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.forms.fields import CharField, ChoiceField
from django.forms.forms import Form
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.entity import load_all_entity_types

class ProjectSetUp(Form):
    name=CharField(required=True)
    entity_type=ChoiceField(label="Entity type", required=True)
    questionnaire_type=CharField(required=True)
    def get_entity_types(self):
            manager = get_db_manager()
            type_dict = load_all_entity_types(manager)
            type_list = [(k, v) for k, v in type_dict.items()]
            return type_list

    def __init__(self, *args, **kwargs):
        super(ProjectSetUp, self).__init__(*args, **kwargs)
        type_list = self.get_entity_types()
        self.fields['entity_type']._set_choices(type_list)

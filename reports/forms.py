from django.forms.fields import CharField
from django.forms.forms import Form

class Report(Form):
    location = CharField()
    entity_type = CharField()
    column_headers = list
    values = dict
    pass

class HierarchyReport(Form):
    entity_type=CharField()
    column_headers =list
    rows = list
    values=list
    pass

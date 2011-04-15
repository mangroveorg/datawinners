from django.forms.fields import CharField
from django.forms.forms import Form

class Report(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    entity_type = CharField(required=True,label='Entity Type')
    column_headers = list
    values = list
    filter = CharField(required=False,label='Filter')

class HierarchyReport(Form):
    entity_type=CharField()
    column_headers =list
    rows = list
    values=list
    pass

# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.forms.fields import CharField
from django.forms.forms import Form


class ReportHierarchy(Form):
    
    aggregate_on_path = CharField(required = True)
    aggregates_field = CharField(required = True)

class Report(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    entity_type = CharField(required=True,label='Entity Type')
    column_headers = list
    values = list
    filter = CharField(required=False,label='Filter')
    


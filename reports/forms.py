# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.forms.fields import CharField, IntegerField, ChoiceField
from django.forms.forms import Form
from django import forms



class ReportHierarchy(Form):
    PATH_CHOICES = (("location", "location"), ("governance", "governance"))
    REDUCE_CHOICES = (("sum", "sum"), ("count", "count"))
    FIELD_CHOICES = (("*", "All"), ("patients", "patients"), ("beds", "beds"), ("meds", "meds"))
    error_css_class = 'error'
    required_css_class = 'required'
    aggregate_on_path = forms.ChoiceField(required=True, widget=forms.Select, choices=PATH_CHOICES)
    aggregates_field = forms.ChoiceField(label="Field", required=True, widget=forms.Select, choices=FIELD_CHOICES)
    reduce = forms.ChoiceField(label="Aggregate Function", required=True, widget=forms.Select, choices=REDUCE_CHOICES)
    level = IntegerField(min_value=1, max_value=3)
    entity_type = ChoiceField(label="Entity type", required=True)

    def __init__(self, choices,*args, **kwargs):
        super(ReportHierarchy, self).__init__(*args, **kwargs)
        self.fields['entity_type'].choices = choices


class Report(Form):
    error_css_class = 'error'
    required_css_class = 'required'
    filter = CharField(required=False, label='Location Filter (e.g India,MH)')
    aggregates_field = CharField(required=True, label="Field")
    entity_type = ChoiceField(label="Entity type", required=True)

    def __init__(self, choices,*args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        self.fields['entity_type'].choices = choices

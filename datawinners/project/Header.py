from django.utils.translation import ugettext
from mangrove.form_model.field import DateField, GeoCodeField
from project.helper import DEFAULT_DATE_FORMAT

class Header(object):
    def __init__(self, form_model):
        prefix = self.prefix()
        prefix_types = [DEFAULT_DATE_FORMAT.lower(), '']
        if form_model.event_time_question:
            prefix = [ugettext("Reporting Period")] + prefix
            prefix_types = [form_model.event_time_question.date_format] + prefix_types

        if form_model.entity_type != ['reporter']:
            prefix = [ugettext(form_model.entity_type[0]).capitalize()] + prefix
            prefix_types = [''] + prefix_types

        field_ = [(field.label, field.date_format if isinstance(field, DateField) else (
                       "gps" if isinstance(field, GeoCodeField)  else "")) for field in form_model.fields[1:] if
                                                                           not field.is_event_time_field]
        self.leading = prefix + [each[0] for each in field_]
        self.questions = prefix_types + [each[1] for each in field_]


    def get(self):
        return self.leading, self.questions

    def prefix(self):
        return [ugettext("Submission Date"), ugettext("Data Sender")]

class AllSubmissionsHeader(Header):
    def prefix(self):
        return [ugettext("Submission Date"), ugettext('Status'), ugettext("Data Sender")]



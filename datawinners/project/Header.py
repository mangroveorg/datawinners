from django.utils.translation import ugettext
from mangrove.form_model.field import DateField, GeoCodeField
from mangrove.utils.json_codecs import encode_json
from datawinners.project.helper import DEFAULT_DATE_FORMAT

class Header(object):
    def __init__(self, form_model):
        self._form_model = form_model
        self._header_list, self._header_type_list = zip(*self._select_header())

    @property
    def info(self):
        return {'header_list': self._header_list, 'header_name_list': repr(encode_json(self._header_list)),
                'header_type_list': repr(encode_json(self._header_type_list))}

    @property
    def header_list(self):
        return self._header_list

    @property
    def header_type_list(self):
        return self._header_type_list


    def _select_header(self):
        return filter(lambda each: each, self._prefix()) + self._fields_header()

    def _prefix(self):
        return [self._id(), self._subject_header(), self._reporting_period_header(), self._submission_date_header(),
                self._data_sender_header()]

    def _submission_date_header(self):
        return ugettext("Submission Date"), DEFAULT_DATE_FORMAT.lower()

    def _data_sender_header(self):
        return ugettext("Data Sender"), ''

    def _reporting_period_header(self):
        rp_field = self._form_model.event_time_question
        return (ugettext("Reporting Period"), rp_field.date_format) if rp_field else None

    def _subject_header(self):
        subject_type = self._form_model.entity_type[0]
        return (ugettext(subject_type).capitalize(), '') if subject_type != 'reporter' else None

    def _fields_header(self):
        return [(field.label, field.date_format if isinstance(field, DateField) else (
            "gps" if isinstance(field, GeoCodeField)  else "")) for field in self._form_model.fields[1:] if
                not field.is_event_time_field]

    def _id(self):
        return "Submission Id", ''


class SubmissionsPageHeader(Header):
    def _status(self):
        return ugettext('Status'), ''


    def _prefix(self):
        return [self._data_sender_header(), self._submission_date_header(), self._status(),
                self._subject_header(), self._reporting_period_header()]
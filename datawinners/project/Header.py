from collections import OrderedDict
from django.utils.translation import ugettext
from datawinners.search.submission_headers import HeaderFactory
from datawinners.search.submission_index_constants import SubmissionIndexConstants
from datawinners.search.submission_index import es_field_name
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


class SubmissionsPageHeader():
    def __init__(self, form_model, submission_type):
        self._form_model = form_model
        self.submission_type = submission_type

    def get_column_title(self):
        header = HeaderFactory(self._form_model).create_header(self.submission_type)
        header_dict = header.get_header_field_dict()
        header_dict.pop('ds_id', None)
        header_dict.pop("entity_short_code", None)
        return header_dict.values()


class SubmissionExcelHeader():
    def __init__(self, form_model, submission_type):
        self._form_model = form_model
        self.submission_type = submission_type

    def add_datasender_id_column(self, header_dict, result):
        result.update({
            SubmissionIndexConstants.DATASENDER_ID_KEY: {
                "label": header_dict[SubmissionIndexConstants.DATASENDER_ID_KEY]}})

    def get_columns(self):
        header = HeaderFactory(self._form_model).create_header(self.submission_type)
        header_dict = header.get_header_field_dict()
        # header_dict = OrderedDict({'name':"Name"}, {"p":"Place", "})
        if self._form_model.entity_type == ["reporter"]:
            header_dict.pop("entity_short_code", None)

        result = OrderedDict()
        for key in header_dict:
            if key != SubmissionIndexConstants.DATASENDER_ID_KEY:
                result.update({key: {"label": header_dict[key]}})
                if key == SubmissionIndexConstants.DATASENDER_NAME_KEY: #add key column after name
                    self.add_datasender_id_column(header_dict, result)

        for field in self._form_model.fields:
            field_name = es_field_name(field.code.lower(), self._form_model.id)
            if result.has_key(field_name):
                result.get(field_name).update({"type": field.type})
                if field.type == "date":
                    result.get(field_name).update({"format": field.date_format})

        return result
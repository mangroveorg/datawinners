from django.utils.translation import ugettext
from mangrove.form_model.field import DateField, GeoCodeField
from datawinners.project.Header import Header

class ExcelFileAnalysisHeader(Header):
    def _prefix(self):
        return [self._id(), self._subject_name_header(), self._subject_id_header(),self._reporting_period_header(),self._submission_date_header(),self._data_sender_name_header(),self._data_sender_id_header()]

    def _subject_name_header(self):
        subject_type = self._form_model.entity_type[0]
        return (ugettext(subject_type).capitalize(), '')  if subject_type != 'reporter' else None

    def _subject_id_header(self):
        subject_type = self._form_model.entity_type[0]
        return (ugettext(subject_type+' Id').capitalize(), '')  if subject_type != 'reporter' else None

    def _data_sender_name_header(self):
        return ugettext("Data Sender Name"), ''

    def _data_sender_id_header(self):
        return ugettext("Data Sender Id"), ''

    def get_field_header_list(self, field):
        if isinstance(field, DateField):
            return [(field.label, field.date_format)]
        else:
            if isinstance(field, GeoCodeField):
                return [(field.label+ " Latitude","gps"),(field.label+" Longitude","gps")]
            else:
                return [(field.label,"")]

    def _fields_header(self):
        header_list = []
        for field in self._form_model.fields[1:]:
            if not field.is_event_time_field:
                header_list.extend(self.get_field_header_list(field))
        return header_list

class ExcelFileSubmissionHeader(ExcelFileAnalysisHeader):
    def _prefix(self):
        return [self._id(), self._data_sender_name_header(), self._data_sender_id_header(),self._submission_date_header(),
                self._status(),self._error_message(),self._subject_name_header(), self._subject_id_header(),self._reporting_period_header()]

    def _status(self):
        return ugettext('Status'), ''

    def _error_message(self):
        return ugettext('Error Messages'), ''


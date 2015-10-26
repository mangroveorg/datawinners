from collections import OrderedDict

from django.utils.translation import ugettext
from datawinners.entity.import_data import get_entity_type_info

from datawinners.search.index_utils import es_unique_id_code_field_name, es_questionnaire_field_name
from datawinners.search.submission_headers import HeaderFactory
from datawinners.search.submission_index_constants import SubmissionIndexConstants
from mangrove.form_model.field import DateField, GeoCodeField, FieldSet
from mangrove.utils.json_codecs import encode_json
from datawinners.project.helper import DEFAULT_DATE_FORMAT
from mangrove.datastore.user_questionnaire_preference import get_user_questionnaire_preference, detect_visibility
from mangrove.form_model.form_model import get_form_model_by_entity_type


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
        return [self._id(), self._subject_header(), self._submission_date_header(),
                self._data_sender_header()]

    def _submission_date_header(self):
        return ugettext("Submission Date"), DEFAULT_DATE_FORMAT.lower()

    def _data_sender_header(self):
        return ugettext("Data Sender"), ''

    def _subject_header(self):
        subject_type = self._form_model.entity_type[0]
        return (ugettext(subject_type).capitalize(), '')

    def _fields_header(self):
        return [(field.label, field.date_format if isinstance(field, DateField) else (
            "gps" if isinstance(field, GeoCodeField)  else "")) for field in self._form_model.fields[1:]]

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
        unique_question_field_names = [es_unique_id_code_field_name(
            es_questionnaire_field_name(field.code, self._form_model.id, field.parent_field_code)) for
                                       field in
                                       self._form_model.entity_questions]
        for field_name in unique_question_field_names:
            header_dict.pop(field_name, None)
        return header_dict.values()


class AnalysisPageHeader():
    def __init__(self, form_model, dbm, user_id):
        self._form_model = form_model
        self._dbm = dbm
        self._user_id = user_id

    def get_column_title(self):
        header = []
        user_questionnaire_preference = get_user_questionnaire_preference(self._dbm, self._user_id, self._form_model.id)

        generic_columns = OrderedDict()

        generic_columns['date'] = ugettext("Submission Date")
        generic_columns['datasender.name'] = ugettext("Data Sender Name")
        generic_columns['datasender.id'] = ugettext("Data Sender Id")
        generic_columns['datasender.mobile_number'] = ugettext("Data Sender Mobile Number")
        generic_columns['datasender.email'] = ugettext("Data Sender Email")
        generic_columns['datasender.location'] = ugettext("Data Sender Location")
        generic_columns['datasender.geo_code'] = ugettext("Data Sender GPS Coordinates")


        for column_id, column_title in generic_columns.iteritems():
            header.append(self._form_column_info(
                column_id, column_title,
                detect_visibility(
                    user_questionnaire_preference,
                    column_id)))

        for field in self._form_model.fields:
            prefix = self._form_model.id + "_" + field.code + "_details"
            if field.is_entity_field:
                entity_type_info = get_entity_type_info(field.unique_id_type, self._dbm)
                # ID Nr mandatory fields, with mandatory order of fields
                # q2 is the name field, q6 is the code field
                expected_mandatory_fields_with_order = ['q2', 'q6']
                for val in expected_mandatory_fields_with_order:
                    if val in entity_type_info['codes']:
                        idx = entity_type_info['codes'].index(val)
                        column_id = prefix + "." + val
                        header.append(self._form_column_info(
                            column_id, entity_type_info['labels'][idx],
                            detect_visibility(
                                user_questionnaire_preference,
                                column_id)))

                for idx, val in enumerate(entity_type_info['codes']):
                    if val not in expected_mandatory_fields_with_order:
                        column_id = prefix + "." + val
                        header.append(self._form_column_info(
                            column_id, entity_type_info['labels'][idx],
                            detect_visibility(
                                user_questionnaire_preference,
                                column_id)))

            else:
                column_id = self._form_model.id + '_' + field.code
                header.append(self._form_column_info(
                    column_id, field.label,
                    detect_visibility(
                        user_questionnaire_preference,
                        column_id)))

        return header

    def _form_column_info(self, column_id, column_title, visibility):
        return {
            "data": column_id,
            "name": column_id,
            "title": column_title,
            "defaultContent": "",
            "visible": visibility
        }


class SubmissionExcelHeader():
    def __init__(self, form_model, submission_type, language='en'):
        self._form_model = form_model
        self.submission_type = submission_type
        self.language = language

    def add_datasender_id_column(self, header_dict, result):
        result.update({
            SubmissionIndexConstants.DATASENDER_ID_KEY: {
                "label": header_dict[SubmissionIndexConstants.DATASENDER_ID_KEY]}})

    def _update_with_field_meta(self, fields, result, header, parent_field_name=None, ):
        for field in fields:
            if isinstance(field, FieldSet) and field.is_group():
                self._update_with_field_meta(field.fields, result, header, field.code)
            else:
                field_name = es_questionnaire_field_name(field.code, self._form_model.id, parent_field_name)

                if result.has_key(field_name):
                    result.get(field_name).update({"type": field.type})
                    if field.type == "date":
                        result.get(field_name).update({"format": field.date_format})
                    if field.type == "field_set":
                        result.get(field_name).update({"fields": self.get_sub_fields_of(field, header),
                                                       "code": field.code,
                                                       'fieldset_type': field.fieldset_type})

    def get_columns(self):
        header = HeaderFactory(self._form_model, self.language).create_header(self.submission_type)
        header_dict = header.get_header_field_dict()
        result = OrderedDict()
        for key in header_dict:
            if key != SubmissionIndexConstants.DATASENDER_ID_KEY:
                result.update({key: {"label": header_dict[key]}})
                if key == SubmissionIndexConstants.DATASENDER_NAME_KEY:  # add key column after name
                    self.add_datasender_id_column(header_dict, result)

        if self.submission_type == 'analysis':
            self._add_type_to_datasender_fields(result)
        self._update_with_field_meta(self._form_model.fields, result, header=header)
        return result

    def _add_type_to_datasender_fields(self, result):
        result.get('datasender.id').update({'type':'short_code'})
        result.get('datasender.name').update({'type':'text'})
        result.get('datasender.email').update({'type':'email'})
        result.get('datasender.location').update({'type':'text'})
        result.get('datasender.geo_code').update({'type':'geocode'})
        result.get('datasender.mobile_number').update({'type':'telephone_number'})
        

    def get_sub_fields_of(self, field, header):
        col = OrderedDict()
        for field in field.fields:
            details = {"type": field.type, "label": field.label}
            col.update({field.code: details})
            if field.type == "date":
                details.update({"format": field.date_format})
            if field.type == 'unique_id':
                header.add_unique_id_field_in_repeat(field, col)
            if field.type == "field_set":
                details.update({"code": field.code})
                details.update({"fields": self.get_sub_fields_of(field, header)})

        return col

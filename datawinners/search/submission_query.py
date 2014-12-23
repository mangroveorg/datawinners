import json
import datetime

from django.utils.translation import ugettext, get_language
import elasticutils
from datawinners.accountmanagement.localized_time import convert_utc_to_localized

from datawinners.search.filters import SubmissionDateRangeFilter, DateQuestionRangeFilter
from datawinners.search.index_utils import es_unique_id_code_field_name, es_questionnaire_field_name
from datawinners.search.submission_headers import HeaderFactory
from datawinners.search.submission_index_constants import SubmissionIndexConstants
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT
from datawinners.search.query import QueryBuilder, Query
from mangrove.form_model.field import FieldSet, SelectField, MediaField
from mangrove.form_model.form_model import get_field_by_attribute_value

class SubmissionQueryResponseCreator(object):
    def __init__(self, form_model, localized_time_delta):
        self.form_model = form_model
        self.localized_time_delta = localized_time_delta

    def combine_name_and_id(self, short_code, entity_name, submission):
        return submission.append(
            ["%s<span class='small_grey'>  %s</span>" % (
                entity_name, short_code)]) if entity_name else submission.append(entity_name)

    def get_field_set_fields(self, fields, parent_field_code=None):
        field_set_field_dict = {}
        for field in fields:
            if isinstance(field, FieldSet):
                field_set_field_dict.update(
                    {es_questionnaire_field_name(field.code, self.form_model.id, parent_field_code): field})
                group_field_code = field.code if field.is_group() else None
                field_set_field_dict.update(self.get_field_set_fields(field.fields, group_field_code))
        return field_set_field_dict

    def _populate_datasender(self, res, submission):
        if res.get(SubmissionIndexConstants.DATASENDER_ID_KEY) == u'N/A':
            submission.append(res.get(SubmissionIndexConstants.DATASENDER_NAME_KEY))
        else:
            self.combine_name_and_id(res.get(SubmissionIndexConstants.DATASENDER_ID_KEY),
                                     res.get(SubmissionIndexConstants.DATASENDER_NAME_KEY), submission)

    def _populate_error_message(self, key, language, res, submission):
        error_msg = res.get(key)
        if error_msg.find('| |') != -1:
            error_msg = error_msg.split('| |,')[['en', 'fr'].index(language)]
        submission.append(error_msg)

    def _convert_to_localized_date_time(self, key, res, submission):
        submission_date_time = datetime.datetime.strptime(res.get(key), "%b. %d, %Y, %I:%M %p")
        datetime_local = convert_utc_to_localized(self.localized_time_delta, submission_date_time)
        submission.append(datetime_local.strftime("%b. %d, %Y, %H:%M"))

    def create_response(self, required_field_names, search_results):
        entity_question_codes = [es_questionnaire_field_name(field.code, self.form_model.id) for field in
                                 self.form_model.entity_questions]
        fieldset_fields = self.get_field_set_fields(self.form_model.fields)
        meta_fields = [SubmissionIndexConstants.DATASENDER_ID_KEY]
        meta_fields.extend([es_unique_id_code_field_name(code) for code in entity_question_codes])

        submissions = []
        language = get_language()
        for res in search_results.hits:
            submission = [res._meta.id]
            for key in required_field_names:
                if not key in meta_fields:
                    if key in entity_question_codes:
                        self.combine_name_and_id(short_code=res.get(es_unique_id_code_field_name(key)),
                                                 entity_name=res.get(key), submission=submission)
                    elif key == SubmissionIndexConstants.DATASENDER_NAME_KEY:
                        self._populate_datasender(res, submission)
                    elif key == 'status':
                        submission.append(ugettext(res.get(key)))
                    elif key == SubmissionIndexConstants.SUBMISSION_DATE_KEY:
                        self._convert_to_localized_date_time(key, res, submission)
                    elif key == 'error_msg':
                        self._populate_error_message(key, language, res, submission)
                    elif key in fieldset_fields.keys():
                        submission.append(
                            _format_fieldset_values_for_representation(res.get(key), fieldset_fields.get(key)))
                    else:
                        submission.append(self.append_if_attachments_are_present(res, key))
            submissions.append(submission)
        return submissions

    def _get_key(self, key):
        if '_' in key:
            return key[key.index('_') + 1:]
        else:
            return key

    def append_if_attachments_are_present(self, res, key):
        if isinstance(get_field_by_attribute_value(self.form_model, 'code', self._get_key(key)), MediaField):
            value = res.get(key)
            if value:
                return "<a href='/download/attachment/%s/%s'>%s</a>" % (res._meta.id, value, value)
        else:
            return res.get(ugettext(key))


def _format_values(field_set, formatted_value, value_list):
    if not value_list:
        return ''
    value_dict = value_list[0]
    for i, field in enumerate(field_set.fields):
        if isinstance(field, SelectField):
            choices = value_dict.get(field.code)
            if choices:
                if field.is_single_select:
                    value = choices
                else:
                    value = '(' + ', '.join(choices) + ')' if len(choices) > 1 else ', '.join(choices)
            else:
                value = ''
        elif isinstance(field, FieldSet):
            value = ''
            value = _format_values(field, value, value_dict.get(field.code))
        else:
            value = value_dict.get(field.code) or ''
        formatted_value += '"' + '<span class="repeat_qtn_label">' + field.label + '</span>' + ': ' + value + '"'
        formatted_value += ';' if i == len(field_set.fields) - 1 else ', '
    return formatted_value


def _format_fieldset_values_for_representation(entry, field_set):
    formatted_value = ''
    if entry:
        for value_dict in json.loads(entry):
            formatted_value = _format_values(field_set, formatted_value, [value_dict])
            formatted_value += '<br><br>'
        return '<span class="repeat_ans">' + formatted_value + '</span>'

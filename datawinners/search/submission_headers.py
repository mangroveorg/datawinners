from abc import abstractmethod
from collections import OrderedDict

from django.utils.translation import ugettext

from datawinners.search.index_utils import es_unique_id_code_field_name, es_questionnaire_field_name
from datawinners.search.submission_index_constants import SubmissionIndexConstants
from datawinners.utils import translate
from mangrove.form_model.form_model import header_fields, get_form_model_by_entity_type, get_form_model_by_code
from mangrove.form_model.project import get_entity_type_fields


class SubmissionHeader():
    def __init__(self, dbm, form_model, language='en'):
        self.dbm = dbm
        self.form_model = form_model
        self.language = language

    def update_datasender_header(self, header_dict):
        header_dict.update(
            {SubmissionIndexConstants.DATASENDER_NAME_KEY: translate("Data Sender", self.language, ugettext)})
        ds_field_names, labels, codes = get_entity_type_fields(self.dbm)
        ds_dict = OrderedDict()
        for field in ds_field_names:
            ds_dict[self.form_model.id + '_reporter.' + field] = field
        header_dict.update(ds_dict)

    def update_datasender_header_for_sort(self, header_list):
        header_list.append(self.form_model.id + '_reporter.name.name')
        ds_field_names, labels, codes = get_entity_type_fields(self.dbm)
        ds_dict = OrderedDict()
        for field in ds_field_names:
            ds_dict[self.form_model.id + '_reporter.' + field + "." + field] = field
        header_list.extend(ds_dict.keys())

    def key_attribute(self, field):
            return field.code

    def get_header_dict(self):
        header_dict = OrderedDict()
        header_dict.update(self.update_static_header_info())
        self.update_datasender_header(header_dict)
        entity_questions = self.form_model.entity_questions
        entity_question_dict = dict((self._get_entity_question_path(field), field) for field in entity_questions)
        headers = header_fields(self.form_model, self.key_attribute)
        for field_code, val in headers.items():
            key = es_questionnaire_field_name(field_code, self.form_model.id)
            if field_code in entity_question_dict.keys():
                self.add_unique_id_field(entity_question_dict.get(field_code), header_dict)
            else:
                header_dict.update({key: val})

        return header_dict

    def get_sort_list(self):
        header_list = []
        header_list.extend(self.update_static_header_info().keys())
        self.update_datasender_header_for_sort(header_list)
        entity_questions = self.form_model.entity_questions
        entity_question_dict = dict((self._get_entity_question_path(field), field) for field in entity_questions)
        headers = header_fields(self.form_model, self.key_attribute)
        for field_code, val in headers.items():
            key = es_questionnaire_field_name(field_code, self.form_model.id)
            if field_code in entity_question_dict.keys():
                self.add_unique_id_field_for_sort(entity_question_dict.get(field_code), header_list)
            else:
                header_list.append(key)

        return header_list

    def _get_entity_question_path(self, field):
        return "%s-%s" % (field.parent_field_code, field.code) if field.parent_field_code else field.code

    def _get_unique_id_details(self, unique_id_field):
        unique_id_model = get_form_model_by_entity_type(self.dbm, [unique_id_field.unique_id_type])
        unique_id_question_code = unique_id_field.code
        unique_id_field_name = es_questionnaire_field_name(unique_id_question_code, self.form_model.id,
                                                           unique_id_field.parent_field_code)
        return unique_id_field_name, unique_id_model

    def _update_unique_id_submission_headers(self, header_dict, unique_id_field, unique_id_field_name, unique_id_model):
        unique_id_headers = header_fields(unique_id_model, key_attribute='code')
        unique_id_submission_headers = OrderedDict()
        for key, val in unique_id_headers.iteritems():
            unique_id_submission_headers[
                unique_id_field_name + '.' + unique_id_model.id + '_' + key] = unique_id_field.unique_id_type + ':' + val
        header_dict.update(unique_id_submission_headers)

    def _update_unique_id_submission_headers_for_sort(self, header_dict, unique_id_field, unique_id_field_name, unique_id_model):
        unique_id_headers = header_fields(unique_id_model, key_attribute='code')
        unique_id_submission_headers = OrderedDict()
        for key, val in unique_id_headers.iteritems():
            unique_id_submission_headers[
                unique_id_field_name + '.' + unique_id_model.id + '_' + key + '.' + unique_id_model.id + '_' + key] = unique_id_field.unique_id_type + ':' + val
        header_dict.extend(unique_id_submission_headers.keys())

    def add_unique_id_field(self, unique_id_field, header_dict):
        unique_id_field_name, unique_id_model = self._get_unique_id_details(unique_id_field)
        header_dict.update({unique_id_field_name: unique_id_field.label})
        #headers of id nr
        self._update_unique_id_submission_headers(header_dict, unique_id_field, unique_id_field_name, unique_id_model)

    def add_unique_id_field_for_sort(self, unique_id_field, header_list):
        unique_id_field_name, unique_id_model = self._get_unique_id_details(unique_id_field)
        header_list.append(unique_id_field_name+'.'+unique_id_model.id+'_q2'+'.'+unique_id_model.id+'_q2')
        #headers of id nr
        self._update_unique_id_submission_headers_for_sort(header_list, unique_id_field, unique_id_field_name, unique_id_model)

    def add_unique_id_field_in_repeat(self, unique_id_field, header_dict):
        unique_id_question_code = unique_id_field.code
        subject_title = unique_id_field.unique_id_type
        header_dict.update({unique_id_question_code+'_unique_code': {'label': "%s ID" % subject_title}})

    def get_header_field_names(self):
        return self.get_header_dict().keys()

    def get_header_field_dict(self):
        return self.get_header_dict()

    def get_field_names_as_header_name(self):
        return self.get_sort_list()

    @abstractmethod
    def update_static_header_info(self):
        pass


class SubmissionAnalysisHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update({"date": translate("Submission Date", self.language, ugettext)})
        # self.update_datasender_header(header_dict)
        return header_dict


class AllSubmissionHeader(SubmissionHeader):


    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update({"date": translate("Submission Date", self.language, ugettext)})
        header_dict.update({"status": translate("Status", self.language, ugettext)})
        # self.update_datasender_header(header_dict)
        return header_dict


class SuccessSubmissionHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update({"date": translate("Submission Date", self.language, ugettext)})
        # self.update_datasender_header(header_dict)
        return header_dict


class MobileSubmissionHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update({SubmissionIndexConstants.DATASENDER_NAME_KEY: "Data Sender"})
        header_dict.update({"date": "Submission Date"})
        return header_dict


class ErroredSubmissionHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update({"date": translate("Submission Date", self.language, ugettext)})
        header_dict.update({"error_msg": translate("Error Message", self.language, ugettext)})
        # self.update_datasender_header(header_dict)
        return header_dict


class HeaderFactory():
    def __init__(self, dbm, form_model, language='en'):
        self.header_to_class_dict = {"all": AllSubmissionHeader, "deleted": AllSubmissionHeader,
                                     "analysis": SubmissionAnalysisHeader,
                                     "success": SuccessSubmissionHeader, "error": ErroredSubmissionHeader,
                                     "mobile": MobileSubmissionHeader}
        self.dbm = dbm
        self.form_model = form_model
        self.language = language

    def create_header(self, submission_type):
        header_class = self.header_to_class_dict.get(submission_type)
        return header_class(self.dbm, self.form_model, self.language)

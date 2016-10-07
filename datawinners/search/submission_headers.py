from abc import abstractmethod
from collections import OrderedDict

from django.utils.translation import ugettext

from datawinners.search.index_utils import es_unique_id_code_field_name, es_questionnaire_field_name
from datawinners.search.submission_index_constants import SubmissionIndexConstants
from datawinners.utils import translate
from mangrove.form_model.form_model import header_fields, EntityFormModel,\
    get_form_model_by_entity_type
from mangrove.form_model.field import FieldSet
from __builtin__ import isinstance


class SubmissionHeader(object):
    def __init__(self, form_model, language='en'):
        self.form_model = form_model
        self.language = language

    def get_header_dict(self):
        header_dict = OrderedDict()
        header_dict.update(self.update_static_header_info())

        def key_attribute(field):
            return field.code

        if isinstance(self.form_model, EntityFormModel):
            entity_questions = self.form_model.base_entity_questions
        else:
            entity_questions = self.form_model.entity_questions
        entity_question_dict = dict((self._get_entity_question_path(field), field) for field in entity_questions)
        headers = header_fields(self.form_model, key_attribute)
        for field_code, val in headers.items():
            if field_code in entity_question_dict.keys():
                self.add_unique_id_field(entity_question_dict.get(field_code), header_dict)
            else:
                key = es_questionnaire_field_name(field_code.replace(".", " "), self.form_model.id)
                header_dict.update({key: val})

        return header_dict
    

    def _get_entity_question_path(self, field):
        return "%s-%s" % (field.parent_field_code, field.code) if field.parent_field_code else field.code

    def add_unique_id_field(self, unique_id_field, header_dict):
        unique_id_question_code = unique_id_field.code
        subject_title = unique_id_field.unique_id_type
        unique_id_field_name = es_questionnaire_field_name(unique_id_question_code, self.form_model.id, unique_id_field.parent_field_code)
        header_dict.update({unique_id_field_name: unique_id_field.label})
        header_dict.update({es_unique_id_code_field_name(unique_id_field_name): "%s ID" % subject_title})

    def add_unique_id_field_in_repeat(self, unique_id_field, header_dict):
        unique_id_question_code = unique_id_field.code
        subject_title = unique_id_field.unique_id_type
        header_dict.update({unique_id_question_code+'_unique_code': {'label': "%s ID" % subject_title}})

    def get_header_field_names(self):
        return self.get_header_dict().keys()

    def get_header_field_dict(self):
        return self.get_header_dict()

    def get_field_names_as_header_name(self):
        headers = self.get_header_dict().keys()
        entity_questions = self.form_model.entity_questions
        for entity_question in entity_questions:
            if not self.form_model.is_part_of_repeat_field(entity_question):
                headers.remove(
                    es_unique_id_code_field_name(es_questionnaire_field_name(entity_question.code, self.form_model.id, entity_question.parent_field_code)))
        return headers

    @abstractmethod
    def update_static_header_info(self):
        pass


class SubmissionAnalysisHeader(SubmissionHeader):
    def __init__(self,form_model, language='en'):
        super(SubmissionAnalysisHeader, self).__init__(form_model, language)
        self.header_dict = OrderedDict()
        self.header_dict.update(self.update_static_header_info())
        self._update_header_dict_from_fields(self.form_model.fields, self.header_dict)
        
    def get_header_dict(self):
        return self.header_dict

    def _update_header_dict_from_fields(self, fields, header_dict, parent_field_code=None):
        for field in fields:
            if field.is_entity_field:
                self.add_unique_id_in_header_dict(header_dict, field, parent_field_code, parent_field_types=[], nested=False)
            elif isinstance(field, FieldSet) and field.is_group():
                self._update_header_dict_from_fields(field.fields, header_dict, field.code)
            else:
                key = es_questionnaire_field_name(field.code.replace(".", " "), self.form_model.id, parent_field_code=parent_field_code)
                header_dict.update({key: field.label})


    def add_unique_id_in_header_dict(self, header_dict, field, parent_field_code=None, parent_field_types=[], nested=False):
        id_number_fields = get_form_model_by_entity_type(self.form_model._dbm, [field.unique_id_type]).fields
        if field.unique_id_type in parent_field_types:
            return None #Helps Prevent cyclic Linked ID Nr
        parent_field_types.append(field.unique_id_type)
        
        if not nested:
            parent_field_code = '_' + parent_field_code + "-" if parent_field_code else "_"
            prefix = self.form_model.id + parent_field_code + field.code + "_details"
        else:
            prefix = parent_field_code + '.' + field.code + '_details'
        
        for nested_field in id_number_fields:
            if nested_field.name != 'entity_type':
                column_id = prefix + "." + nested_field.code
                header_dict.update({column_id: nested_field.label})
            if nested_field.type in ['unique_id']:
                self.add_unique_id_in_header_dict(
                                                  header_dict, 
                                                  nested_field, 
                                                  parent_field_code=prefix, 
                                                  parent_field_types=parent_field_types,
                                                  nested=True)
            
    def update_static_header_info(self):
        header_dict = OrderedDict()

        header_dict.update({"date": translate("Submission Date", self.language, ugettext)})
        header_dict.update(
            {'datasender.id': translate("Data Sender Id", self.language, ugettext)})
        header_dict.update(
            {'datasender.name': translate("Data Sender Name", self.language, ugettext)})
        header_dict.update(
            {'datasender.mobile_number': translate("Data Sender Mobile Number", self.language, ugettext)})
        header_dict.update(
            {'datasender.email': translate("Data Sender Email", self.language, ugettext)})
        header_dict.update(
            {'datasender.location': translate("Data Sender Location", self.language, ugettext)})
        header_dict.update(
            {'datasender.geo_code': translate("Data Sender GPS Coordinates", self.language, ugettext)})
        return header_dict


class AllSubmissionHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update(
            {SubmissionIndexConstants.DATASENDER_ID_KEY: translate("Data Sender Id", self.language, ugettext)})
        header_dict.update(
            {SubmissionIndexConstants.DATASENDER_NAME_KEY: translate("Data Sender Name", self.language, ugettext)})
        header_dict.update({"date": translate("Submission Date", self.language, ugettext)})
        if not hasattr(self.form_model,'is_poll') or self.form_model.is_poll is False:
            header_dict.update({"status": translate("Status", self.language, ugettext)})

        return header_dict

class IdentificationNumberHeader(SubmissionHeader):
    def update_static_header_info(self):
        return OrderedDict()

class SuccessSubmissionHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update(
            {SubmissionIndexConstants.DATASENDER_ID_KEY: translate("Data Sender Id", self.language, ugettext)})
        header_dict.update(
            {SubmissionIndexConstants.DATASENDER_NAME_KEY: translate("Data Sender Name", self.language, ugettext)})
        header_dict.update({"date": translate("Submission Date", self.language, ugettext)})
        return header_dict


class DuplicatesSubmissionHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update(
            {SubmissionIndexConstants.DATASENDER_ID_KEY: translate("Data Sender Id", self.language, ugettext)})
        header_dict.update(
            {SubmissionIndexConstants.DATASENDER_NAME_KEY: translate("Data Sender Name", self.language, ugettext)})
        header_dict.update({"date": translate("Submission Date", self.language, ugettext)})
        if not self.form_model.is_poll:
            header_dict.update({"status": translate("Status", self.language, ugettext)})
        return header_dict


class MobileSubmissionHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update({SubmissionIndexConstants.DATASENDER_NAME_KEY: "Data Sender Name"})
        header_dict.update({"date": "Submission Date"})
        return header_dict


class ErroredSubmissionHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update(
            {SubmissionIndexConstants.DATASENDER_ID_KEY: translate("Data Sender Id", self.language, ugettext)})
        header_dict.update(
            {SubmissionIndexConstants.DATASENDER_NAME_KEY: translate("Data Sender Name", self.language, ugettext)})
        header_dict.update({"date": translate("Submission Date", self.language, ugettext)})
        header_dict.update({"error_msg": translate("Error Message", self.language, ugettext)})
        return header_dict


class HeaderFactory():
    def __init__(self, form_model, language='en'):
        self.header_to_class_dict = {"all": AllSubmissionHeader, "deleted": AllSubmissionHeader,
                                     "analysis": SubmissionAnalysisHeader,
                                     "success": SuccessSubmissionHeader, "error": ErroredSubmissionHeader,
                                     "duplicates": DuplicatesSubmissionHeader,
                                     "mobile": MobileSubmissionHeader,
                                     "identification_number":IdentificationNumberHeader,
                                     }
        self.form_model = form_model
        self.language = language

    def create_header(self, submission_type):
        if submission_type is None:
            header_class = AllSubmissionHeader
        else:
            header_class = self.header_to_class_dict.get(submission_type)
        return header_class(self.form_model, self.language)

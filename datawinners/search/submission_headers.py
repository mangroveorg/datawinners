from abc import abstractmethod
from collections import OrderedDict

from django.utils.translation import ugettext

from datawinners.search.index_utils import es_unique_id_code_field_name, es_questionnaire_field_name
from datawinners.search.submission_index_constants import SubmissionIndexConstants
from datawinners.utils import translate
from mangrove.form_model.form_model import header_fields


class SubmissionHeader():
    def __init__(self, form_model, language='en'):
        self.form_model = form_model
        self.language = language

    def get_header_dict(self):
        header_dict = OrderedDict()
        header_dict.update(self.update_static_header_info())

        def key_attribute(field):
            return field.code

        entity_questions = self.form_model.entity_questions
        entity_question_dict = dict((field.code, field) for field in entity_questions)
        headers = header_fields(self.form_model, key_attribute)
        for field_code, val in headers.items():
            key = es_questionnaire_field_name(field_code, self.form_model.id)
            if field_code in entity_question_dict.keys():
                self.add_unique_id_field(entity_question_dict.get(field_code), header_dict)
            else:
                header_dict.update({key: val})

        return header_dict

    def add_unique_id_field(self, unique_id_field, header_dict):
        unique_id_question_code = unique_id_field.code
        subject_title = unique_id_field.unique_id_type
        unique_id_field_name = es_questionnaire_field_name(unique_id_question_code, self.form_model.id)
        header_dict.update({unique_id_field_name: unique_id_field.label})
        header_dict.update({es_unique_id_code_field_name(unique_id_field_name): "%s ID" % subject_title})

    def get_header_field_names(self):
        return self.get_header_dict().keys()

    def get_header_field_dict(self):
        return self.get_header_dict()

    def get_field_names_as_header_name(self):
        headers = self.get_header_dict().keys()
        entity_questions = self.form_model.entity_questions
        for entity_question in entity_questions:
            headers.remove(self.form_model.id+'_'+es_unique_id_code_field_name(entity_question.code))
        return headers

    @abstractmethod
    def update_static_header_info(self):
        pass


class SubmissionAnalysisHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()

        header_dict.update({"date": translate("Submission Date", self.language, ugettext)})
        header_dict.update({SubmissionIndexConstants.DATASENDER_ID_KEY: translate("Datasender Id", self.language, ugettext)})
        header_dict.update({SubmissionIndexConstants.DATASENDER_NAME_KEY: translate("Data Sender", self.language, ugettext)})
        return header_dict


class AllSubmissionHeader(SubmissionHeader):

    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update({SubmissionIndexConstants.DATASENDER_ID_KEY: translate("Datasender Id", self.language, ugettext)})
        header_dict.update({SubmissionIndexConstants.DATASENDER_NAME_KEY: translate("Data Sender", self.language, ugettext)})
        header_dict.update({"date": translate("Submission Date", self.language, ugettext)})
        header_dict.update({"status": translate("Status", self.language, ugettext)})

        return header_dict


class SuccessSubmissionHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update({SubmissionIndexConstants.DATASENDER_ID_KEY: translate("Datasender Id", self.language, ugettext)})
        header_dict.update({SubmissionIndexConstants.DATASENDER_NAME_KEY: translate("Data Sender", self.language, ugettext)})
        header_dict.update({"date": translate("Submission Date", self.language, ugettext)})
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
        header_dict.update({SubmissionIndexConstants.DATASENDER_ID_KEY: translate("Datasender Id", self.language, ugettext)})
        header_dict.update({SubmissionIndexConstants.DATASENDER_NAME_KEY: translate("Data Sender", self.language, ugettext)})
        header_dict.update({"date": translate("Submission Date", self.language, ugettext)})
        header_dict.update({"error_msg": translate("Error Message", self.language, ugettext)})
        return header_dict


class HeaderFactory():
    def __init__(self, form_model, language='en'):
        self.header_to_class_dict = {"all": AllSubmissionHeader, "deleted": AllSubmissionHeader,
                                     "analysis": SubmissionAnalysisHeader,
                                     "success": SuccessSubmissionHeader, "error": ErroredSubmissionHeader,
                                     "mobile": MobileSubmissionHeader}
        self.form_model = form_model
        self.language = language

    def create_header(self, submission_type):
        header_class = self.header_to_class_dict.get(submission_type)
        return header_class(self.form_model, self.language)

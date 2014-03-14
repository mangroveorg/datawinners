from abc import abstractmethod
from collections import OrderedDict
from datawinners.search.index_utils import es_field_name
from datawinners.search.submission_index_constants import SubmissionIndexConstants
from mangrove.form_model.form_model import header_fields


class SubmissionHeader():
    def __init__(self, form_model):
        self.form_model = form_model

    def get_header_dict(self):
        header_dict = OrderedDict()
        header_dict.update(self.update_static_header_info())

        def key_attribute(field):
            return field.code.lower()

        headers = header_fields(self.form_model, key_attribute)
        for field_code, val in headers.items():
            key = es_field_name(field_code, self.form_model.id)
            if not header_dict.has_key(key): header_dict.update({key: val})

        #if self.form_model.is_entity_type_reporter():
        #    # For summary projects there will be an extra datasender info question(code eid).
        #    # This condition removes that extra question.
        #    header_dict.pop(es_field_name(self.form_model.entity_question.code, self.form_model.id))
        #    header_dict.pop('entity_short_code')
        return header_dict

    def get_header_field_names(self):
        return self.get_header_dict().keys()

    def get_header_field_dict(self):
        return self.get_header_dict()

    @abstractmethod
    def update_static_header_info(self):
        pass


class SubmissionAnalysisHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        subject_title = self.form_model.entity_type[0].title()
        if self.form_model.unique_id_field:
            header_dict.update({es_field_name(self.form_model.entity_question.code, self.form_model.id): subject_title})
        header_dict.update({'entity_short_code': "%s ID" % subject_title})
        if self.form_model.event_time_question:
            header_dict.update(
                {es_field_name(self.form_model.event_time_question.code, self.form_model.id): "Reporting Date"})

        header_dict.update({"date": "Submission Date"})
        header_dict.update({SubmissionIndexConstants.DATASENDER_ID_KEY: "Datasender Id"})
        header_dict.update({SubmissionIndexConstants.DATASENDER_NAME_KEY: "Datasender Name"})
        return header_dict


class AllSubmissionHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update({SubmissionIndexConstants.DATASENDER_ID_KEY: "Datasender Id"})
        header_dict.update({SubmissionIndexConstants.DATASENDER_NAME_KEY: "Datasender Name"})
        header_dict.update({"date": "Submission Date"})
        header_dict.update({"status": "Status"})
        subject_title = self.form_model.entity_type[0].title()
        if self.form_model.unique_id_field:
            header_dict.update({es_field_name(self.form_model.unique_id_field.code, self.form_model.id): subject_title})
        header_dict.update({'entity_short_code': "%s ID" % subject_title})
        if self.form_model.event_time_question:
            header_dict.update(
                {es_field_name(self.form_model.event_time_question.code, self.form_model.id): "Reporting Date"})

        return header_dict


class SuccessSubmissionHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update({SubmissionIndexConstants.DATASENDER_ID_KEY: "Datasender Id"})
        header_dict.update({SubmissionIndexConstants.DATASENDER_NAME_KEY: "Datasender Name"})
        header_dict.update({"date": "Submission Date"})
        subject_title = self.form_model.entity_type[0].title()
        if self.form_model.unique_id_field:
            header_dict.update({es_field_name(self.form_model.entity_question.code, self.form_model.id): subject_title})
        header_dict.update({'entity_short_code': "%s ID" % subject_title})
        if self.form_model.event_time_question:
            header_dict.update(
                {es_field_name(self.form_model.event_time_question.code, self.form_model.id): "Reporting Date"})
        return header_dict


class ErroredSubmissionHeader(SubmissionHeader):
    def update_static_header_info(self):
        header_dict = OrderedDict()
        header_dict.update({SubmissionIndexConstants.DATASENDER_ID_KEY: "Datasender Id"})
        header_dict.update({SubmissionIndexConstants.DATASENDER_NAME_KEY: "Datasender Name"})
        header_dict.update({"date": "Submission Date"})
        header_dict.update({"error_msg": "Error Message"})
        subject_title = self.form_model.entity_type[0].title()
        if self.form_model.unique_id_field:
            header_dict.update({es_field_name(self.form_model.entity_question.code, self.form_model.id): subject_title})
        header_dict.update({'entity_short_code': "%s ID" % subject_title})
        if self.form_model.event_time_question:
            header_dict.update(
                {es_field_name(self.form_model.event_time_question.code, self.form_model.id): "Reporting Date"})
        return header_dict


class HeaderFactory():
    def __init__(self, form_model):
        self.header_to_class_dict = {"all": AllSubmissionHeader, "deleted": AllSubmissionHeader,
                                     "analysis": SubmissionAnalysisHeader,
                                     "success": SuccessSubmissionHeader, "error": ErroredSubmissionHeader}
        self.form_model = form_model

    def create_header(self, submission_type):
        header_class = self.header_to_class_dict.get(submission_type)
        return header_class(self.form_model)
from collections import OrderedDict
from django.utils.translation import gettext
from datawinners.entity.import_data import tabulate_failures, translate_errors

class ImportSubmissionValidator():

    def __init__(self, manager, form_model, project):
        self.manager = manager
        self.form_model = form_model
        self.field_code_label_dict = self.get_field_code_label_dict()
        self.project = project
        self.subject_ids, self.datasender_ids = self._get_subject_or_datasender_ids()

    def validate_rows(self, parsed_rows):
        valid_rows, invalid_row_details = [], []
        row_count = 1
        for row in parsed_rows:
            row_count += 1
            question_code, answer = row.items()[0]
            errors = self._verify_uploaded_id(question_code, answer)
            if not errors:
                cleaned_data, errors = self.form_model.validate_submission(values=row)
            errors_translated = translate_errors(items=errors.items(), question_dict=self.field_code_label_dict, question_answer_dict=row)
            invalid_row_details.append({"errors":errors_translated,"row_count":row_count}) if len(errors) > 0 else valid_rows.append(row)
        return valid_rows, invalid_row_details

    def _verify_uploaded_id(self, q_code, imported_id):
        errors = None
        if self.project.is_summary_project():
            if imported_id not in self.datasender_ids:
                errors = OrderedDict([(q_code, gettext("datasender id not matched"))])
        else:
            if imported_id not in self.subject_ids:
                errors = OrderedDict([(q_code, gettext("subject id not matched"))])
        return errors

    def _get_subject_or_datasender_ids(self):
        subject_ids, datasender_ids = None, None
        if self.project.is_summary_project():
            datasender_ids = [ds['short_code'] for ds in self.project.get_data_senders(self.manager)]
        else:
            entity_type = self.project.entity_type
            start_key = [[entity_type]]
            end_key = [[entity_type], {}, {}]
            rows = self.manager.database.view("entity_name_by_short_code/entity_name_by_short_code", startkey=start_key,endkey=end_key).rows
            subject_ids = [item["key"][1] for item in rows]
        return subject_ids, datasender_ids

    def get_field_code_label_dict(self):
        field_code_label_dict = {}
        for form_field in self.form_model.form_fields:
            label = form_field.get('label')
            quoted_label = '&#39;' + label + '&#39;'
            field_code_label_dict.update({form_field.get('code'):quoted_label})
        return field_code_label_dict





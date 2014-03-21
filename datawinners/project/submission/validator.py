from collections import OrderedDict
from datawinners.entity.import_data import translate_errors
from mangrove.utils.types import is_empty


class SubmissionWorkbookRowValidator():

    def __init__(self, manager, form_model):
        self.manager = manager
        self.form_model = form_model

    def validate_rows(self, parsed_rows):
        field_code_label_dict = self.form_model.get_field_code_label_dict()
        valid_rows, invalid_row_details = [], []
        row_count = 1
        for row in parsed_rows:
            row_count += 1
            #if len([value for value in dict(row).values() if not is_empty(value)]) == 1:
            #    continue
            errors = {}
            unique_id_fields = self.form_model.entity_questions
            for field in unique_id_fields:
                entity_key = field.code
                entity_answer = row.get(entity_key)
                errors.update(self._verify_uploaded_id(entity_key, entity_answer, field))
            cleaned_data, field_errors = self.form_model.validate_submission(values=row)
            errors.update(field_errors)
            errors_translated = translate_errors(items=errors.items(), question_dict=field_code_label_dict, question_answer_dict=row)
            invalid_row_details.append({"errors":errors_translated,"row_count":row_count}) if len(errors) > 0 else valid_rows.append(row)
        return valid_rows, invalid_row_details

    def _verify_uploaded_id(self, q_code, imported_id, unique_id_field):
        subject_ids = self._get_unique_ids(unique_id_field)
        if imported_id not in subject_ids:
            return {q_code: "The unique ID of the Subject does not match any existing Subject ID. Please correct and import again."}

    def _get_unique_ids(self, unique_id_field):
        unique_id_type = unique_id_field.unique_id_type
        start_key = [[unique_id_type]]
        end_key = [[unique_id_type], {}, {}]
        rows = self.manager.database.view("entity_name_by_short_code/entity_name_by_short_code", startkey=start_key,endkey=end_key).rows
        subject_ids = [item["key"][1] for item in rows]
        return subject_ids





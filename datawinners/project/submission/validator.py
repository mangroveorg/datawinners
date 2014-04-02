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
            errors = {}
            cleaned_data, field_errors = self.form_model.validate_submission(values=row)
            errors.update(field_errors)
            errors_translated = translate_errors(items=errors.items(), question_dict=field_code_label_dict, question_answer_dict=row)
            invalid_row_details.append({"errors": errors_translated,"row_count": row_count}) if len(errors) > 0 else valid_rows.append(row)
        return valid_rows, invalid_row_details





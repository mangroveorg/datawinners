from datawinners.entity.import_data import translate_errors





class SubmissionWorkbookRowValidator():

    def __init__(self, manager, form_model):
        self.manager = manager
        self.form_model = form_model

    def _validate_datasender(self, row):
        datasender = row.get('dsid', '')
        user_dsid = row.get('user_dsid', '')
        if datasender and datasender not in self.form_model.data_senders:
            if user_dsid == datasender:
                message = "You are not authorized to submit to this Questionnaire. Add yourself as a Data Sender to the Questionnaire."
            else:
                message = "The Data Sender you are submitting on behalf of cannot submit to this Questionnaire. Add the Data Sender to the Questionnaire."
            return {"datasender": message}
        return {}

    def validate_rows(self, parsed_rows):
        field_code_label_dict = self.form_model.get_field_code_label_dict()
        valid_rows, invalid_row_details = [], []
        row_count = 1
        for row in parsed_rows:
            row_count += 1
            errors = self._validate_datasender(row)
            cleaned_data, field_errors = self.form_model.validate_submission(values=row)
            errors.update(field_errors)
            errors_translated = translate_errors(items=errors.items(), question_dict=field_code_label_dict, question_answer_dict=row)
            invalid_row_details.append({"errors": errors_translated,"row_count": row_count}) if len(errors) > 0 else valid_rows.append(row)
        return valid_rows, invalid_row_details





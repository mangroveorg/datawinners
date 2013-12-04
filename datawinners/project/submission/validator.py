class ImportSubmissionValidator():

    def __init__(self, manager, form_model):
        self.manager = manager
        self.form_model = form_model

    def validate_rows(self, parsed_rows):
        valid_rows, invalid_rows = [], []
        for row in parsed_rows:
            current_row = row[1]
            cleaned_data, errors = self.form_model.validate_submission(values=current_row)
            invalid_rows.append(current_row) if len(errors) > 0 else valid_rows.append(current_row)
        return valid_rows, invalid_rows
from mangrove.form_model.field import SelectField, FieldSet
from mangrove.form_model.xform import remove_node

from datawinners.blue.rules.rule import Rule


class RemoveRule(Rule):
    def remove(self, parent_node, node, xform, old_field, activity_log_detail):
        if isinstance(old_field, FieldSet):
            return

        if node is not None:
            remove_node(parent_node, node)
            xform.remove_bind_node(node)
            xform.remove_instance_node(parent_node, node)
        else:
            xform.remove_bind_node_given_name(old_field.code)
            xform.remove_instance_node_given_name(parent_node, old_field.code)

        if isinstance(old_field, SelectField) and old_field.is_cascade:
            xform.remove_translation_nodes(node)
            xform.remove_cascade_instance_node(node)

        self.fields.append(old_field)
        activity_log_detail["deleted"] = [old_field.label] if activity_log_detail.get("deleted") is None \
            else activity_log_detail.get("deleted") + [old_field.label]

    def update_submission(self, submission):
        if not self.fields:
            return False

        for field in self.fields:
            _check_and_remove_field_from_submission(submission.values, field)
        return True

    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        pass


def _check_and_remove_field_from_submission(submission_values, field_code):
    if field_code in submission_values:
        del submission_values[field_code]
    elif isinstance(submission_values, list):
        for submission in submission_values:
            _check_and_remove_field_from_submission(submission, field_code)
    elif isinstance(submission_values, dict):
        for key, submission in submission_values.items():
            _check_and_remove_field_from_submission(submission, field_code)

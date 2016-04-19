from mangrove.form_model.field import SelectField
from mangrove.form_model.xform import remove_node

from datawinners.blue.rules.rule import Rule


class RemoveRule(Rule):
    def remove(self, parent_node, node, xform, old_field, activity_log_detail):
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
            if hasattr(submission.values, field.code):
                del submission.values[field.code]
        return True

    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        pass

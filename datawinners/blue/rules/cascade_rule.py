from mangrove.form_model.field import SelectField

from datawinners.blue.rules.rule import Rule


class CascadeRule(Rule):
    def update_submission(self, submission):
        pass

    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        if not isinstance(new_field, SelectField) or not new_field.is_cascade:
            return

        old_xform.remove_translation_nodes(node)
        for translation_node in new_xform.get_translation_nodes(node):
            old_xform.add_translation_node(translation_node)

        old_xform.remove_cascade_instance_node(node)
        instance_node = new_xform.get_cascade_instance_node(node)
        if instance_node is not None:
            old_xform.add_cascade_instance_node(instance_node)

    def remove(self, parent_node, node, xform, old_field, activity_log_detail):
        pass

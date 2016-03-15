from mangrove.form_model.xform import add_attrib

from datawinners.blue.rules.rule import Rule


class EditConstraintMessageRule(Rule):
    def add(self, parent_node, node, bind_node, instance_node, xform):
        pass

    def edit(self, node, old_field, new_field, xform):
        bind_node = xform.bind_node(node)
        if bind_node is not None and new_field.constraint_message != old_field.constraint_message:
            add_attrib(bind_node, 'constraintMsg', new_field.constraint_message)

    def update_submission(self, submission):
        return False

    def remove(self, parent_node, node, xform):
        pass

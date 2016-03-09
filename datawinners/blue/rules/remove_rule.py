from mangrove.form_model.xform import remove_node

from datawinners.blue.rules.rule import Rule


class RemoveRule(Rule):
    def remove(self, parent_node, node, xform):
        remove_node(parent_node, node)
        xform.remove_bind_node(node)
        xform.remove_instance_node(parent_node, node)

    def update_submission(self, submission):
        return True

    def change_mapping(self):
        return True

    def edit(self, node, old_field, new_field, xform):
        pass
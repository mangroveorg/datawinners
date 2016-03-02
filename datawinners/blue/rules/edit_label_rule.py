from datawinners.blue.rules.edit_rule import EditRule


class EditLabelRule(EditRule):

    def update_node(self, node, old_field, new_field):
        if new_field and new_field.label != old_field.label:
            node.text = new_field.label

    def tagname(self):
        return 'label'

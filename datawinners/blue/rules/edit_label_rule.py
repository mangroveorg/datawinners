from datawinners.blue.rules.rule import Rule


class EditLabelRule(Rule):

    def apply(self):
        pass

    def edit(self, node, old_field, new_field):
        if new_field and new_field.label != old_field.label:
            node.text = new_field.label

    def tagname(self):
        return 'label'

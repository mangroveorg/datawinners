from datawinners.blue.rules.rule import Rule


class EditDefaultRule(Rule):
    def update_submission(self, submission):
        return False

    def edit(self, node, old_field, new_field, old_xform, new_xform):
        instance_node = old_xform.instance_node(node)
        if new_field.default:
            instance_node.text = new_field.default
        else:
            instance_node.text = new_field.default if instance_node.text and len(instance_node.text.strip()) else instance_node.text

    def remove(self, parent_node, node, xform):
        pass

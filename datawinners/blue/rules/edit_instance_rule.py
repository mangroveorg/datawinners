from datawinners.blue.rules.rule import Rule


class EditDefaultRule(Rule):
    def add(self, parent_node, node, bind_node, instance_node, xform):
        pass

    def update_submission(self, submission):
        return False

    def edit(self, node, old_field, new_field, xform):
        instance_node = xform.instance_node(node)
        if new_field.default:
            instance_node.text = new_field.default
        else:
            instance_node.text = new_field.default if instance_node.text and len(instance_node.text.strip()) else instance_node.text

    def remove(self, parent_node, node, xform):
        pass

    def change_mapping(self):
        return False

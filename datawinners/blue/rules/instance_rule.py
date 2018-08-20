from datawinners.blue.rules.rule import Rule


class EditDefaultRule(Rule):
    def update_submission(self, submission):
        return False

    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        instance_node = old_xform.instance_node(node)
        if new_field.default or instance_node.text and len(instance_node.text.strip()):
            instance_node.text = new_field.default
            activity_log_detail["default_changed"] = [old_field.label] if activity_log_detail.get("default_changed") is None \
                else activity_log_detail.get("default_changed") + [old_field.label]

    def remove(self, parent_node, node, xform, old_field, activity_log_detail):
        pass

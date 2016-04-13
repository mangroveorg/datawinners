import abc

from mangrove.form_model.xform import add_child, remove_node

from datawinners.blue.rules.rule import Rule


class NodeRule(Rule):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update_node(self, node, old_field, new_field, activity_log_detail):
        pass

    @abc.abstractmethod
    def tagname(self):
        pass

    @abc.abstractmethod
    def create_node(self, node, old_field, new_field, activity_log_detail):
        pass

    @abc.abstractmethod
    def remove_node(self, parent_node, node, new_field, old_field, activity_log_detail):
        pass

    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        node_to_be_updated = [child for child in node if child.tag.endswith(self.tagname())]
        if node_to_be_updated:
            self.update_node(node_to_be_updated[0], old_field, new_field, activity_log_detail)
            self.remove_node(node, node_to_be_updated[0], new_field, old_field, activity_log_detail)
        else:
            self.create_node(node, old_field, new_field, activity_log_detail)

    def remove(self, parent_node, node, xform, old_field, activity_log_detail):
        pass

    def update_submission(self, submission):
        return False


class EditLabelRule(NodeRule):
    def remove_node(self, parent_node, node, new_field, old_field, activity_log_detail):
        pass

    def create_node(self, node, old_field, new_field, activity_log_detail):
        pass

    def update_node(self, node, old_field, new_field, activity_log_detail):
        if new_field.label != old_field.label:
            node.text = new_field.label
            activity_log_detail["changed"] = [old_field.label] if activity_log_detail.get("changed") is None \
                else activity_log_detail.get("changed") + [old_field.label]

    def tagname(self):
        return 'label'


class EditHintRule(NodeRule):
    def remove_node(self, parent_node, node, new_field, old_field, activity_log_detail):
        if not new_field.hint and old_field.hint:
            remove_node(parent_node, node)
            activity_log_detail["hint_changed"] = [old_field.label] if activity_log_detail.get("hint_changed") is None \
                else activity_log_detail.get("hint_changed") + [old_field.label]

    def create_node(self, node, old_field, new_field, activity_log_detail):
        if old_field.hint != new_field.hint:
            add_child(node, self.tagname(), new_field.hint)
            activity_log_detail["hint_changed"] = [old_field.label] if activity_log_detail.get("hint_changed") is None \
                else activity_log_detail.get("hint_changed") + [old_field.label]

    def update_node(self, node, old_field, new_field, activity_log_detail):
        if new_field.hint is not None and new_field.hint != old_field.hint:
            node.text = new_field.hint
            activity_log_detail["hint_changed"] = [old_field.label] if activity_log_detail.get("hint_changed") is None \
                else activity_log_detail.get("hint_changed") + [old_field.label]

    def tagname(self):
        return 'hint'

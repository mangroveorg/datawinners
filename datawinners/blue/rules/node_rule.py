import abc

from mangrove.form_model.xform import add_child, remove_node

from datawinners.blue.rules.rule import Rule


class NodeRule(Rule):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update_node(self, node, old_field, new_field):
        pass

    @abc.abstractmethod
    def tagname(self):
        pass

    @abc.abstractmethod
    def create_node(self, node, old_field, new_field):
        pass

    @abc.abstractmethod
    def remove_node(self, parent_node, node, new_field, old_field):
        pass

    def edit(self, node, old_field, new_field, old_xform, new_xform):
        node_to_be_updated = [child for child in node if child.tag.endswith(self.tagname())]
        if node_to_be_updated:
            self.update_node(node_to_be_updated[0], old_field, new_field)
            self.remove_node(node, node_to_be_updated[0], new_field, old_field)
        else:
            self.create_node(node, old_field, new_field)

    def remove(self, parent_node, node, xform):
        pass

    def update_submission(self, submission):
        return False


class EditLabelRule(NodeRule):
    def remove_node(self, parent_node, node, new_field, old_field):
        pass

    def create_node(self, node, old_field, new_field):
        pass

    def update_node(self, node, old_field, new_field):
        if new_field.label != old_field.label:
            node.text = new_field.label

    def tagname(self):
        return 'label'


class EditHintRule(NodeRule):
    def remove_node(self, parent_node, node, new_field, old_field):
        if not new_field.hint and old_field.hint:
            remove_node(parent_node, node)

    def create_node(self, node, old_field, new_field):
        if old_field.hint != new_field.hint:
            add_child(node, self.tagname(), new_field.hint)

    def update_node(self, node, old_field, new_field):
        if new_field.hint != old_field.hint:
            node.text = new_field.hint

    def tagname(self):
        return 'hint'

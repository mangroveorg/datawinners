import abc

from mangrove.form_model.xform import add_child

from datawinners.blue.rules.rule import Rule


class EditRule(Rule):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update_node(self, param, old_field, new_field):
        pass

    @abc.abstractmethod
    def tagname(self):
        pass

    def _create_node(self, node, field):
        if getattr(field, self.tagname()):
            add_child(node, self.tagname(), getattr(field, self.tagname()))

    def edit(self, node, old_field, new_field):
        node_to_be_updated = [child for child in node if child.tag.endswith(self.tagname())]
        if node_to_be_updated:
            self.update_node(node_to_be_updated[0], old_field, new_field)
        else:
            self._create_node(node, new_field)

    def remove(self):
        pass

    def change_mapping(self):
        return False

    def update_submission(self, submission):
        return False


class EditLabelRule(EditRule):
    def update_node(self, node, old_field, new_field):
        if new_field and new_field.label != old_field.label:
            node.text = new_field.label

    def tagname(self):
        return 'label'


class EditHintRule(EditRule):
    def update_node(self, node, old_field, new_field):
        if new_field and new_field.hint != old_field.hint:
            node.text = new_field.hint

    def tagname(self):
        return 'hint'

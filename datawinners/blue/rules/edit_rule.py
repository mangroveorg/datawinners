import abc

from datawinners.blue.rules.rule import Rule


class EditRule(Rule):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update_node(self, param, old_field, new_field):
        pass

    @abc.abstractmethod
    def tagname(self):
        pass

    def edit(self, node, old_field, new_field):
        node_to_be_updated = [child for child in node if child.tag.endswith(self.tagname())]
        self.update_node(node_to_be_updated[0], old_field, new_field)

    def remove(self):
        pass

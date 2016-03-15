from datawinners.blue.rules.bind_rule import ConstraintMessageRule
from datawinners.blue.rules.edit_instance_rule import EditDefaultRule
from datawinners.blue.rules.edit_node_attribute_rule import EditAppearanceRule
from datawinners.blue.rules.edit_rule import EditLabelRule, EditHintRule

REGISTERED_RULES = [EditLabelRule(), EditHintRule(), ConstraintMessageRule(), EditAppearanceRule(), EditDefaultRule()]

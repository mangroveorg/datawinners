from datawinners.blue.rules.bind_rule import EditConstraintMessageRule
from datawinners.blue.rules.instance_rule import EditDefaultRule
from datawinners.blue.rules.node_attribute_rule import EditAppearanceRule
from datawinners.blue.rules.edit_rule import EditLabelRule, EditHintRule

REGISTERED_RULES = [EditLabelRule(), EditHintRule(), EditConstraintMessageRule(), EditAppearanceRule(), EditDefaultRule()]

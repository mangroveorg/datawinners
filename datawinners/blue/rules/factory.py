from datawinners.blue.rules.bind_rule import ConstraintMessageRule
from datawinners.blue.rules.edit_rule import EditLabelRule, EditHintRule
from datawinners.blue.rules.remove_rule import RemoveRule


def get_all_rules():
    return [EditLabelRule(), EditHintRule(), ConstraintMessageRule(), RemoveRule()]
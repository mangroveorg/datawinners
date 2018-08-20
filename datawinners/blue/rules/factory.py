from datawinners.blue.rules.add_rule import AddRule
from datawinners.blue.rules.bind_rule import EditConstraintMessageRule, EditRequiredRule, EditConstraintRule, \
    EditRelevantRule
from datawinners.blue.rules.cascade_rule import CascadeRule
from datawinners.blue.rules.choice_rule import ChoiceRule
from datawinners.blue.rules.instance_rule import EditDefaultRule
from datawinners.blue.rules.node_attribute_rule import EditAppearanceRule
from datawinners.blue.rules.node_rule import EditLabelRule, EditHintRule
from datawinners.blue.rules.note_rule import NoteRule
from datawinners.blue.rules.remove_rule import RemoveRule


def get_all_rules():
    return [EditLabelRule(), EditHintRule(), EditConstraintMessageRule(), RemoveRule(), AddRule(), EditAppearanceRule(),
            EditDefaultRule(), EditRequiredRule(), EditConstraintRule(), EditRelevantRule(), ChoiceRule(), CascadeRule(),
            NoteRule()]


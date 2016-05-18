from datawinners.blue.rules.rule import Rule
from mangrove.form_model.field import SelectField
from mangrove.form_model.xform import child_nodes, node_has_child, update_node, remove_node, add_child


class ChoiceRule(Rule):
    def update_submission(self, submission):
        pass

    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        if not isinstance(new_field, SelectField) or new_field.is_cascade:
            return

        for new_option in new_field.options:
            old_option = [old_option for old_option in old_field.options if new_option['val'] == old_option['val']]
            if not old_option:
                self._add_node(node, new_option)
                activity_log_detail["choice_changed"] = [old_field.label] if activity_log_detail.get("choice_changed") is None \
                    else activity_log_detail.get("choice_changed") if old_field.label in activity_log_detail.get("choice_changed") \
                    else activity_log_detail.get("choice_changed") + [old_field.label]

        for old_option in old_field.options:
            new_option = [new_option for new_option in new_field.options if new_option['val'] == old_option['val']]
            if new_option:
                if new_option[0]['text'] != old_option['text']:
                    self._update_node(node, new_option[0])
                    activity_log_detail["choice_changed"] = [old_field.label] if activity_log_detail.get("choice_changed") is None \
                        else activity_log_detail.get("choice_changed") if old_field.label in activity_log_detail.get("choice_changed") \
                        else activity_log_detail.get("choice_changed") + [old_field.label]
            else:
                self._remove_node(node, old_option)
                activity_log_detail["choice_changed"] = [old_field.label] if activity_log_detail.get("choice_changed") is None \
                    else activity_log_detail.get("choice_changed") if old_field.label in activity_log_detail.get("choice_changed") \
                    else activity_log_detail.get("choice_changed") + [old_field.label]

    def _add_node(self, node, new_option):
        item_node = add_child(node, 'item', '')
        add_child(item_node, 'label', new_option['text'])
        add_child(item_node, 'value', new_option['val'])

    def _update_node(self, node, new_option):
        node_to_be_updated = self._item_node(node, new_option['val'])
        update_node(node_to_be_updated, 'label', new_option['text'])

    def _remove_node(self, node, old_option):
        remove_node(node, self._item_node(node, old_option['val']))

    def _item_node(self, node, value):
        item_nodes = child_nodes(node, 'item')
        return [item for item in item_nodes if node_has_child(item, 'value', value)][0]

    def remove(self, parent_node, node, xform, old_field, activity_log_detail):
        pass

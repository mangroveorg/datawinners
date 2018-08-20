import abc

from mangrove.form_model.xform import add_attrib, remove_attrib

from datawinners.blue.rules.rule import Rule


class EditAppearanceRule(Rule):

    def remove(self, parent_node, node, xform, old_field, activity_log_detail):
        pass

    def update_submission(self, submission):
        return False

    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        if bool(new_field.appearance) and node.get("appearance") != new_field.appearance:
            add_attrib(node, "appearance", new_field.appearance)
            activity_log_detail["appearance_changed"] = [old_field.label] if activity_log_detail.get("appearance_changed") is None \
                else activity_log_detail.get("appearance_changed") + [old_field.label]

        if not bool(new_field.appearance) and bool(node.get("appearance")):
            remove_attrib(node, "appearance")
            activity_log_detail["appearance_changed"] = [old_field.label] if activity_log_detail.get("appearance_changed") is None \
                else activity_log_detail.get("appearance_changed") + [old_field.label]

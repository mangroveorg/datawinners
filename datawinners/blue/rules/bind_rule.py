import abc
import re

from mangrove.form_model.xform import add_attrib, remove_attrib, replace_node_name_with_xpath

from datawinners.blue.rules.rule import Rule


class EditBindRule(Rule):
    __metaclass__ = abc.ABCMeta

    def update_submission(self, submission):
        pass

    def remove(self, parent_node, node, xform, old_field, activity_log_detail):
        pass


class EditConstraintMessageRule(EditBindRule):

    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        bind_node = old_xform.bind_node(node)

        if bind_node is not None and new_field.constraint_message != old_field.constraint_message:
            if new_field.constraint_message:
                add_attrib(bind_node, 'constraintMsg', new_field.constraint_message)
            else:
                remove_attrib(bind_node, 'constraintMsg')
            activity_log_detail["constraint_message_changed"] = [old_field.label] if activity_log_detail.get("constraint_message_changed") is None \
                else activity_log_detail.get("constraint_message_changed") + [old_field.label]


class EditConstraintRule(EditBindRule):

    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        bind_node = old_xform.bind_node(node)

        if bind_node is not None and new_field.xform_constraint != old_field.xform_constraint:
            xform_constraint = new_field.xform_constraint
            if xform_constraint:
                if "${" in xform_constraint:
                    xform_constraint = replace_node_name_with_xpath(xform_constraint, old_xform)
                add_attrib(bind_node, 'constraint', xform_constraint)
            else:
                remove_attrib(bind_node, 'constraint')
            activity_log_detail["constraint_changed"] = [old_field.label] if activity_log_detail.get("constraint_changed") is None \
                else activity_log_detail.get("constraint_changed") + [old_field.label]


class EditRequiredRule(EditBindRule):

    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        bind_node = old_xform.bind_node(node)

        if bind_node is not None:
            if new_field.is_required() and not old_field.is_required():
                add_attrib(bind_node, 'required', 'true()')
                activity_log_detail["required_changed"] = [old_field.label] if activity_log_detail.get("required_changed") is None \
                    else activity_log_detail.get("required_changed") + [old_field.label]
            elif not new_field.is_required() and old_field.is_required():
                remove_attrib(bind_node, 'required')
                activity_log_detail["required_changed"] = [old_field.label] if activity_log_detail.get("required_changed") is None \
                    else activity_log_detail.get("required_changed") + [old_field.label]


class EditRelevantRule(EditBindRule):

    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        bind_node = old_xform.bind_node(node)

        if bind_node is not None and new_field.relevant != old_field.relevant:
            if new_field.relevant:
                relevant = replace_node_name_with_xpath(new_field.relevant, old_xform)
                add_attrib(bind_node, 'relevant', relevant)
            else:
                remove_attrib(bind_node, 'relevant')
            activity_log_detail["relevant_changed"] = [old_field.label] if activity_log_detail.get("relevant_changed") is None \
                else activity_log_detail.get("relevant_changed") + [old_field.label]


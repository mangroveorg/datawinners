import xml.etree.ElementTree as ET

from mangrove.form_model.xform import add_node, get_node

from datawinners.blue.rules.rule import Rule


class NoteRule(Rule):
    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        pass

    def update_submission(self, submission):
        pass

    def update_xform(self, old_questionnaire, new_questionnaire, activity_log_detail):
        old_xform = old_questionnaire.xform_model
        new_xform = new_questionnaire.xform_model
        self._update_xform(new_questionnaire.fields, old_questionnaire.fields,
                           old_xform.get_body_node(), old_xform, new_xform, activity_log_detail)

        old_questionnaire.xform = '<?xml version="1.0" encoding="utf-8"?>%s' % ET.tostring(old_xform.root_node)

    def _update_xform(self, new_fields, old_fields, parent_node, old_xform, new_xform, activity_log_detail):
        for bind_node in old_xform.get_readonly_bind_nodes():
            old_xform.remove_bind_node(bind_node)
            old_xform.remove_instance_node_given_bind_node(bind_node)
            old_xform.remove_node_given_bind_node(bind_node)

        for bind_node in new_xform.get_readonly_bind_nodes():
            old_xform.add_bind_node(bind_node)
            parent_node, node = new_xform.node_given_bind_node(bind_node)
            parent_instance_node, instance_node = new_xform.instance_node_given_bind_node(bind_node)
            parent_node = old_xform.get_body_node() if parent_node == new_xform.get_body_node() else parent_node
            old_xform.add_node_given_parent_node(parent_node, node)
            old_xform.add_instance_node(parent_node, instance_node)
            add_node(parent_node, node)

    def remove(self, parent_node, node, xform, old_field, activity_log_detail):
        pass

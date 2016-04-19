import xml.etree.ElementTree as ET

from mangrove.form_model.field import FieldSet, SelectField
from mangrove.form_model.xform import get_node, add_node

from datawinners.blue.rules.rule import Rule


class AddRule(Rule):
    def add(self, parent_node, node, bind_node, instance_node, xform):
        if node is not None:
            add_node(parent_node, node)
        xform.add_bind_node(bind_node)
        xform.add_instance_node(parent_node, instance_node)

    def remove(self, parent_node, node, xform, old_field, activity_log_detail):
        pass

    def update_xform(self, old_questionnaire, new_questionnaire, activity_log_detail):
        old_xform_model = old_questionnaire.xform_model
        new_xform_model = new_questionnaire.xform_model
        self._update_xform_with_new_fields(new_questionnaire.fields, old_questionnaire.fields,
                                           new_xform_model.get_body_node(), old_xform_model.get_body_node(),
                                           old_xform_model, new_xform_model, activity_log_detail)

        old_questionnaire.xform = '<?xml version="1.0" encoding="utf-8"?>%s' % ET.tostring(old_xform_model.root_node)

    def _update_xform_with_new_fields(self, new_fields, old_fields, new_parent_node, old_parent_node, old_xform,
                                      new_xform, activity_log_detail):
        for new_field in new_fields:
            new_node = get_node(new_parent_node, new_field.code)
            old_field = [old_field for old_field in old_fields if old_field.code == new_field.code]
            if old_field:
                if isinstance(new_field, FieldSet):
                    old_node = get_node(old_parent_node, new_field.code)
                    self._update_xform_with_new_fields(new_field.fields, old_field[0].fields, new_node, old_node,
                                                       old_xform, new_xform, activity_log_detail)
            else:
                bind_node = new_xform.get_bind_node_by_name(new_field.code) if new_node is None else new_xform.bind_node(new_node)
                instance_node = new_xform.instance_node_given_name(new_field.code) if new_node is None else new_xform.instance_node(new_node)
                self.add(old_parent_node, new_node, bind_node, instance_node, old_xform)
                if isinstance(new_field, SelectField) and new_field.is_cascade:
                    for translation_node in new_xform.get_translation_nodes(new_node):
                        old_xform.add_translation_node(translation_node)
                    old_xform.add_cascade_instance_node(new_xform.get_cascade_instance_node(new_node))

                activity_log_detail["added"] = [new_field.label] if activity_log_detail.get("added") is None \
                    else activity_log_detail.get("added") + [new_field.label]

    def update_submission(self, submission):
        return False

    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        pass

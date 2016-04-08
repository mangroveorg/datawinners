import xml.etree.ElementTree as ET

from mangrove.form_model.field import FieldSet
from mangrove.form_model.xform import get_node, add_node

from datawinners.blue.rules.rule import Rule


class AddRule(Rule):
    def add(self, parent_node, node, bind_node, instance_node, xform):
        add_node(parent_node, node)
        xform.add_bind_node(bind_node)
        xform.add_instance_node(parent_node, instance_node)

    def remove(self, parent_node, node, xform):
        pass

    def update_xform(self, old_questionnaire, new_questionnaire):
        old_xform_model = old_questionnaire.xform_model
        new_xform_model = new_questionnaire.xform_model
        self._update_xform_with_new_fields(new_questionnaire.fields, old_questionnaire.fields,
                                           new_xform_model.get_body_node(), old_xform_model.get_body_node(),
                                           old_xform_model, new_xform_model)

        old_questionnaire.xform = '<?xml version="1.0" encoding="utf-8"?>%s' % ET.tostring(old_xform_model.root_node)

    def _update_xform_with_new_fields(self, new_fields, old_fields, new_parent_node, old_parent_node, old_xform, new_xform):
        for new_field in new_fields:
            new_node = get_node(new_parent_node, new_field.code)
            old_field = [old_field for old_field in old_fields if old_field.code == new_field.code]
            if old_field:
                if isinstance(new_field, FieldSet):
                    old_node = get_node(old_parent_node, new_field.code)
                    self._update_xform_with_new_fields(new_field.fields, old_field[0].fields, new_node, old_node, old_xform, new_xform)
            else:
                self.add(old_parent_node, new_node, new_xform.bind_node(new_node), new_xform.instance_node(new_node), old_xform)

    def update_submission(self, submission):
        return False

    def edit(self, node, old_field, new_field, old_xform, new_xform):
        pass

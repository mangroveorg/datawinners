from datawinners.blue.rules.rule import Rule
import xml.etree.ElementTree as ET

from mangrove.form_model.field import FieldSet, SelectField
from mangrove.form_model.xform import get_node, add_node, add_node_before_another_node

class EditRepeatCountRule(Rule):

    def add(self, parent_node, node, bind_node, instance_node, xform):
        if node is not None:
            add_node(parent_node, node)
        xform.add_bind_node(bind_node)
        xform.add_instance_node(parent_node, instance_node)

    def remove(self, parent_node, node, xform, old_field, activity_log_detail):
        pass


    def edit(self, node, old_field, new_field, old_xform, new_xform, activity_log_detail):
        pass

    def remove(self, parent_node, node, xform, old_field, activity_log_detail):
        pass

    def update_submission(self, submission):
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
            if hasattr(new_field, 'is_calculated') and new_field.is_calculated and new_field.name.endswith("_count"):
                repeat_field_code = new_field.name[:-6]
                new_node = get_node(new_parent_node, new_field.code)
                old_repeat_count_field = None
                old_repeat_field = None
                for old_field in old_fields:
                    if old_field.code == new_field.code:
                        old_repeat_count_field = old_field
                    if old_field.code == repeat_field_code:
                        old_repeat_field = old_field
                        
                if old_repeat_count_field: #update the repeat count value
                    if isinstance(new_field, FieldSet):
                        old_node = get_node(old_parent_node, new_field.code)
                        self._update_xform_with_new_fields(new_field.fields, old_field[0].fields, new_node, old_node,
                                                       old_xform, new_xform, activity_log_detail)
                elif old_repeat_field:#insert node
                    old_repeat_node = get_node(old_parent_node, old_repeat_field.code)
                    bind_node = new_xform.get_bind_node_by_name(new_field.code) if new_node is None else new_xform.bind_node(new_node)
                    old_repeat_bind_node = old_xform.get_bind_node_by_name("my_name")
                    instance_node = new_xform.instance_node_given_name(new_field.code).next() if new_node is None else new_xform.instance_node(new_node)
                    repeat_instance_node = old_xform.instance_node_given_name(repeat_field_code).next()
                    old_xform.add_bind_node_before_another_bind_node(old_repeat_bind_node, bind_node)
                    old_xform.add_instance_node_before_another_one(old_parent_node, repeat_instance_node, instance_node)

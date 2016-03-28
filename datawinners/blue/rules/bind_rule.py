import abc
import re

from mangrove.form_model.xform import add_attrib, remove_attrib

from datawinners.blue.rules.rule import Rule


class EditBindRule(Rule):
    __metaclass__ = abc.ABCMeta

    def update_submission(self, submission):
        pass

    def add(self, parent_node, node, bind_node, instance_node, xform):
        pass

    def remove(self, parent_node, node, xform):
        pass


class EditConstraintMessageRule(EditBindRule):

    def edit(self, node, old_field, new_field, xform):
        bind_node = xform.bind_node(node)

        if bind_node is not None and new_field.constraint_message != old_field.constraint_message and new_field.constraint_message:
            add_attrib(bind_node, 'constraintMsg', new_field.constraint_message)

        if bind_node is not None and new_field.constraint_message != old_field.constraint_message and not new_field.constraint_message:
            remove_attrib(bind_node, 'constraintMsg')


class EditConstraintRule(EditBindRule):

    def edit(self, node, old_field, new_field, xform):
        bind_node = xform.bind_node(node)

        if bind_node is not None and new_field.xform_constraint != old_field.xform_constraint and new_field.xform_constraint:
            xform_constraint = new_field.xform_constraint
            if "${" in new_field.xform_constraint:
                xform_constraint = self.replace_variable_with_xpath(new_field, xform)
            add_attrib(bind_node, 'constraint', xform_constraint)

        if bind_node is not None and new_field.xform_constraint != old_field.xform_constraint and not new_field.xform_constraint:
            remove_attrib(bind_node, 'constraint')

    def replace_variable_with_xpath(self, new_field, xform):
        form_code = re.search('\$\{(.*?)\}', new_field.xform_constraint).group(1)
        constraint_xpath = xform.get_bind_node_by_name(form_code).attrib['nodeset']
        return re.sub(r'(\$\{)(.*?)(\})', " " + constraint_xpath + " ", new_field.xform_constraint)


class EditRequiredRule(EditBindRule):

    def edit(self, node, old_field, new_field, xform):
        bind_node = xform.bind_node(node)

        if bind_node is not None and new_field.is_required() and not old_field.is_required():
            add_attrib(bind_node, 'required', 'true()')

        if bind_node is not None and not new_field.is_required() and old_field.is_required():
            remove_attrib(bind_node, 'required')

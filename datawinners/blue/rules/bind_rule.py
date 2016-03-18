import abc

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


class EditRequiredRule(EditBindRule):

    def edit(self, node, old_field, new_field, xform):
        bind_node = xform.bind_node(node)

        if bind_node is not None and new_field.is_required() and not old_field.is_required():
            add_attrib(bind_node, 'required', 'true()')

        if bind_node is not None and not new_field.is_required() and old_field.is_required():
            remove_attrib(bind_node, 'required')

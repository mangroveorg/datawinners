import abc
import xml.etree.ElementTree as ET

from mangrove.form_model.field import FieldSet
from mangrove.form_model.xform import get_node


class Rule(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.fields = []

    def update_xform(self, old_questionnaire, new_questionnaire):
        xform = old_questionnaire.xform_model
        self._update_xform(new_questionnaire.fields, old_questionnaire.fields, xform.get_body_node(), xform)

        old_questionnaire.xform = '<?xml version="1.0" encoding="utf-8"?>%s' % ET.tostring(xform.root_node)

    def _update_xform(self, new_fields, old_fields, parent_node, xform):
        for old_field in old_fields:
            if hasattr(old_field, 'is_calculated') and old_field.is_calculated:
                continue

            node = get_node(parent_node, old_field.code)
            new_field = [new_field for new_field in new_fields if new_field.code == old_field.code]
            if new_field:
                if isinstance(old_field, FieldSet):
                    self._update_xform(new_field[0].fields, old_field.fields, node, xform)
                self.edit(node, old_field, new_field[0], xform)
            else:
                self.remove(parent_node, node, xform)
                self.fields.append(old_field)

    @abc.abstractmethod
    def remove(self, parent_node, node, xform):
        pass

    @abc.abstractmethod
    def add(self, parent_node, node, bind_node, instance_node, xform):
        pass

    @abc.abstractmethod
    def edit(self, node, old_field, new_field, xform):
        pass

    @abc.abstractmethod
    def update_submission(self, submission):
        pass

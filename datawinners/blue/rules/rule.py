import abc
import xml.etree.ElementTree as ET

from mangrove.form_model.field import FieldSet


class Rule(object):
    __metaclass__ = abc.ABCMeta

    def update_xform(self, old_questionnaire, new_questionnaire):
        xform = old_questionnaire.xform_model
        self._update_xform(new_questionnaire.fields, old_questionnaire.fields, xform,  xform.get_body_node())

        old_questionnaire.xform = '<?xml version="1.0" encoding="utf-8"?>%s' % ET.tostring(xform.root_node)

    def _update_xform(self, new_fields, old_fields, xform, parent_node):
        for old_field in old_fields:
            node = xform.get_node(parent_node, old_field.code)
            new_field = [new_field for new_field in new_fields if new_field.code == old_field.code]

            if isinstance(old_field, FieldSet):
                self._update_xform(new_field[0].fields, old_field.fields, xform, node)

            node_to_be_updated = [child for child in node if child.tag.endswith(self.tagname())]
            self.edit(node_to_be_updated[0], old_field, new_field[0])

    @abc.abstractmethod
    def edit(self, param, old_field, new_field):
        return

    @abc.abstractmethod
    def tagname(self):
        return

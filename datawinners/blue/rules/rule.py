import abc

import xml.etree.ElementTree as ET


class Rule(object):
    __metaclass__ = abc.ABCMeta

    def update_xform(self, old_questionnaire, new_questionnaire):
        for old_field in old_questionnaire.fields:
            new_field = [new_field for new_field in new_questionnaire.fields if new_field.name == old_field.name]
            ET.register_namespace('', 'http://www.w3.org/2002/xforms')
            root_node = ET.fromstring(old_questionnaire.xform)
            html_body_node = root_node._children[1]
            node = old_questionnaire.get_node(html_body_node, old_field)
            node_to_be_updated = [child for child in node if child.tag.endswith(self.tagname())]

            self.edit(node_to_be_updated[0], old_field, new_field[0])
            
            old_questionnaire.xform = '<?xml version="1.0" encoding="utf-8"?>%s' % ET.tostring(root_node)

    @abc.abstractmethod
    def edit(self, param, old_field, new_field):
        return

    @abc.abstractmethod
    def tagname(self):
        return

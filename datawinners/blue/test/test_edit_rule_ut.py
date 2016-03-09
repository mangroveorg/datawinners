import os
import unittest

from mangrove.datastore.documents import ProjectDocument
from mangrove.form_model.field import Field, FieldSet
from mangrove.form_model.project import Project
from mangrove.form_model.tests.test_form_model_unit_tests import DatabaseManagerStub

from datawinners.blue.rules import EditLabelRule, EditHintRule, ConstraintMessageRule
from datawinners.blue.rules.remove_rule import RemoveRule

DIR = os.path.dirname(__file__)


class TestEditRule(unittest.TestCase):

    def test_should_update_xform_with_label_change(self):
        edit_label_rule = EditLabelRule()
        self.maxDiff = None

        old_questionnaire = self.get_questionnaire(group_label="Enter the outer group details",
                                                   group_name="group_outer",
                                                   field_label="Name please",
                                                   field_name="text2")
        new_questionnaire = self.get_questionnaire(group_label="Enter the new outer group details",
                                                   group_name="group_outer",
                                                   field_label="Full name please",
                                                   field_name="text2")
        edit_label_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_hint_change(self):
        edit_hint_rule = EditHintRule()
        self.maxDiff = None

        old_questionnaire = self.get_questionnaire(group_label="Enter the outer group details",
                                                   group_name="group_outer",
                                                   field_label="Name please",
                                                   field_name="text2",
                                                   hint="Enter your name")
        new_questionnaire = self.get_questionnaire(group_label="Enter the outer group details",
                                                   group_name="group_outer",
                                                   field_label="Name please",
                                                   field_name="text2",
                                                   hint="Please enter your name")
        edit_hint_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_insert_hint_node_if_not_existing(self):
        edit_hint_rule = EditHintRule()
        self.maxDiff = None

        old_questionnaire = self.get_questionnaire(group_label="Enter the outer group details",
                                                   group_name="group_outer",
                                                   field_label="Name please",
                                                   field_name="text2")
        new_questionnaire = self.get_questionnaire(group_label="Enter the outer group details",
                                                   group_name="group_outer",
                                                   field_label="Name please",
                                                   field_name="text2",
                                                   hint="Please enter your name")
        edit_hint_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_constraint_message_change(self):
        edit_constraint_message_rule = ConstraintMessageRule()
        self.maxDiff = None

        old_questionnaire = self.get_questionnaire(group_label="Enter the outer group details",
                                                   group_name="group_outer",
                                                   field_label="Name please",
                                                   field_name="text2")
        new_questionnaire = self.get_questionnaire(group_label="Enter the outer group details",
                                                   group_name="group_outer",
                                                   field_label="Name please",
                                                   field_name="text2",
                                                   constraint_message="Please enter your name")
        edit_constraint_message_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_remove_field_change(self):
        remove_rule = RemoveRule()
        self.maxDiff = None

        old_questionnaire = self.get_questionnaire(group_label="Enter the outer group details",
                                                   group_name="group_outer",
                                                   field_label="Name please",
                                                   field_name="text2")
        new_questionnaire = self.get_questionnaire_with_field_removed()

        remove_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def get_questionnaire(self, group_label="Enter the outer group details", group_name="group_outer",
                          field_label="Name please", field_name="text2", hint=None, constraint_message=None):
        field = Field(code=field_name, name=field_name, label=field_label, parent_field_code=group_name)
        field.hint = hint
        field.constraint_message = constraint_message

        doc = ProjectDocument()
        doc.xform = self.get_xform(group_label, field)
        questionnaire = Project.new_from_doc(DatabaseManagerStub(), doc)
        questionnaire.name = "q1"
        questionnaire.form_code = "007"
        questionnaire.fields.append(
            FieldSet(code=group_name, name=group_name, label=group_label, field_set=[field])
        )
        return questionnaire

    def get_questionnaire_with_field_removed(self, group_label="Enter the outer group details", group_name="group_outer"):
        doc = ProjectDocument()
        doc.xform = self.get_xform(group_label)
        questionnaire = Project.new_from_doc(DatabaseManagerStub(), doc)
        questionnaire.name = "q1"
        questionnaire.form_code = "007"
        questionnaire.fields.append(
            FieldSet(code=group_name, name=group_name, label=group_label, field_set=[])
        )
        return questionnaire

    def get_xform(self, group_label, field=None):
        field_attrs = {"instance_node": "", "bind_node": "", "input_node": ""}
        if field:
            hint_node = '<hint>' + field.hint + '</hint>' if field.hint else ''
            input_node = '<input ref="/tmpkWhV2m/group_outer/' + field.name + '"><label>' + field.label + '</label>' + hint_node + '</input>'
            constraint_message_attr = 'constraintMsg="' + field.constraint_message + '" ' if field.constraint_message else ''
            bind_node = '<bind ' + constraint_message_attr + 'nodeset="/tmpkWhV2m/group_outer/' + field.name + '" required="true()" type="string" />'
            instance_node = '<' + field.name + ' />'
            field_attrs = {"instance_node": instance_node, "bind_node": bind_node, "input_node": input_node}
        return (('<?xml version="1.0" encoding="utf-8"?><html:html xmlns="http://www.w3.org/2002/xforms" xmlns:html="http://www.w3.org/1999/xhtml">\
              <html:head>\
                <html:title>q1</html:title>\
                <model>\
                  <instance>\
                    <tmpkWhV2m id="tmpkWhV2m">\
                      <group_outer>\
                        <number1 />\
                        <group_inner>\
                          <number2 />\
                          <text1 />\
                          <number3 />\
                          <people />\
                          <clinic />\
                        </group_inner>\
                        {instance_node}</group_outer>\
                      <meta>\
                        <instanceID />\
                      </meta>\
                    </tmpkWhV2m>\
                  </instance>\
                  <bind nodeset="/tmpkWhV2m/group_outer/number1" required="true()" type="int" />\
                  <bind nodeset="/tmpkWhV2m/group_outer/group_inner/number2" required="true()" type="int" />\
                  <bind nodeset="/tmpkWhV2m/group_outer/group_inner/text1" required="true()" type="string" />\
                  <bind nodeset="/tmpkWhV2m/group_outer/group_inner/number3" required="true()" type="int" />\
                  <bind nodeset="/tmpkWhV2m/group_outer/group_inner/people" type="select1" />\
                  <bind nodeset="/tmpkWhV2m/group_outer/group_inner/clinic" type="select1" />\
                  {bind_node}<bind calculate="concat(''uuid:'', uuid())" nodeset="/tmpkWhV2m/meta/instanceID" readonly="true()" type="string" />\
                </model>\
              </html:head>\
              <html:body>\
                <group ref="/tmpkWhV2m/group_outer">\
                  <label>' + group_label + '</label>\
                  <input ref="/tmpkWhV2m/group_outer/number1">\
                    <label>Lucky number</label>\
                  </input>\
                  <group ref="/tmpkWhV2m/group_outer/group_inner">\
                    <label>Enter the inner group details</label>\
                    <input ref="/tmpkWhV2m/group_outer/group_inner/number2">\
                      <label>Favourite number</label>\
                    </input>\
                    <input ref="/tmpkWhV2m/group_outer/group_inner/text1">\
                      <label>Favourite colour</label>\
                    </input>\
                    <input ref="/tmpkWhV2m/group_outer/group_inner/number3">\
                      <label>How many friends have you got?</label>\
                    </input>\
                    <select1 ref="/tmpkWhV2m/group_outer/group_inner/people">\
                      <label>Enter the city</label>\
                      <item>\
                        <label>placeholder</label>\
                        <value>people</value>\
                      </item>\
                    </select1>\
                    <select1 ref="/tmpkWhV2m/group_outer/group_inner/clinic">\
                      <label>Enter the doctor</label>\
                      <item>\
                        <label>placeholder</label>\
                        <value>clinic</value>\
                      </item>\
                    </select1>\
                  </group>\
                  {input_node}</group>\
              </html:body>\
            </html:html>').format(**field_attrs))

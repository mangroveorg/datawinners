import os
import unittest

from mangrove.datastore.documents import ProjectDocument
from mangrove.form_model.field import Field, FieldSet
from mangrove.form_model.project import Project
from mangrove.form_model.tests.test_form_model_unit_tests import DatabaseManagerStub

from datawinners.blue.rules.instance_rule import EditDefaultRule
from datawinners.blue.rules.node_rule import EditLabelRule, EditHintRule
from datawinners.blue.rules.add_rule import AddRule
from datawinners.blue.rules.bind_rule import EditConstraintMessageRule, EditRequiredRule
from datawinners.blue.rules.node_attribute_rule import EditAppearanceRule
from datawinners.blue.rules.remove_rule import RemoveRule

DIR = os.path.dirname(__file__)


class TestEditRule(unittest.TestCase):

    def test_should_update_xform_with_label_change(self):
        edit_label_rule = EditLabelRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2")
        new_questionnaire = self._get_questionnaire(group_label="Enter the new outer group details",
                                                    group_name="group_outer",
                                                    field_label="Full name please",
                                                    field_name="text2")
        edit_label_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_hint_change(self):
        edit_hint_rule = EditHintRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    hint="Enter your name")
        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    hint="Please enter your name")
        edit_hint_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_insert_hint_node_if_not_existing(self):
        edit_hint_rule = EditHintRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2")
        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    hint="Please enter your name")
        edit_hint_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_remove_hint_node(self):
        edit_hint_rule = EditHintRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    hint="Please enter your name")
        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2")
        edit_hint_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_appearance_change(self):
        edit_appearance_rule = EditAppearanceRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    appearance="multiline")
        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2")
        edit_appearance_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2")
        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    appearance="multiline")
        edit_appearance_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    appearance="sample")
        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    appearance="multiline")
        edit_appearance_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_default_change(self):
        edit_default_rule = EditDefaultRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    default="18.31")
        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2")
        edit_default_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2")
        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    default="18.31")
        edit_default_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    default="15")
        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    default="18.31")
        edit_default_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_required_to_optional_change(self):
        edit_default_rule = EditRequiredRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    required=True)

        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2")
        edit_default_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_optional_to_required_change(self):
        edit_default_rule = EditRequiredRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2")

        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    required=True)
        edit_default_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_constraint_message_change(self):
        edit_constraint_message_rule = EditConstraintMessageRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2")
        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    constraint_message="Please enter your name")
        edit_constraint_message_rule.update_xform(old_questionnaire=old_questionnaire,
                                                  new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    constraint_message="Please enter your name")
        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2")
        edit_constraint_message_rule.update_xform(old_questionnaire=old_questionnaire,
                                                  new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    constraint_message="Please enter your name")
        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2",
                                                    constraint_message="Updated Please enter your name")
        edit_constraint_message_rule.update_xform(old_questionnaire=old_questionnaire,
                                                  new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_remove_field_change(self):
        remove_rule = RemoveRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2")
        new_questionnaire = self._get_questionnaire_with_field_removed()

        remove_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_add_field_change(self):
        add_rule = AddRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire_with_field_removed()
        new_questionnaire = self._get_questionnaire(group_label="Enter the outer group details",
                                                    group_name="group_outer",
                                                    field_label="Name please",
                                                    field_name="text2")

        add_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def _get_questionnaire(self, group_label="Enter the outer group details", group_name="group_outer",
                           field_label="Name please", field_name="text2", hint=None, constraint_message=None,
                           appearance=None, default=None, required=False):
        field = Field(code=field_name, name=field_name, label=field_label, parent_field_code=group_name, hint=hint,
                      constraint_message=constraint_message, appearance=appearance, default=default, required=required)
        repeat = FieldSet(code="repeat_outer", name="repeat_outer", label="Enter the details you wanna repeat", field_set=[field])
        doc = ProjectDocument()
        doc.xform = self._get_xform(group_label, field)
        questionnaire = Project.new_from_doc(DatabaseManagerStub(), doc)
        questionnaire.name = "q1"
        questionnaire.form_code = "007"
        questionnaire.fields.append(
            FieldSet(code=group_name, name=group_name, label=group_label, field_set=[repeat])
        )
        return questionnaire

    def _get_questionnaire_with_field_removed(self, group_label="Enter the outer group details",
                                              group_name="group_outer"):
        repeat = FieldSet(code="repeat_outer", name="repeat_outer", label="Enter the details you wanna repeat", field_set=[])
        doc = ProjectDocument()
        doc.xform = self._get_xform(group_label)
        questionnaire = Project.new_from_doc(DatabaseManagerStub(), doc)
        questionnaire.name = "q1"
        questionnaire.form_code = "007"
        questionnaire.fields.append(
            FieldSet(code=group_name, name=group_name, label=group_label, field_set=[repeat])
        )
        return questionnaire

    def _get_xform(self, group_label, field=None):
        field_attrs = {"instance_node": "", "bind_node": "", "input_node": '<repeat nodeset="/tmpRTha_7/repeat_outer" />'}
        if field:
            hint_node = '<hint>' + field.hint + '</hint>' if field.hint else ''
            appearance_attr = 'appearance="' + field.appearance + '" ' if field.appearance else ''
            input_node = '<repeat nodeset="/tmpRTha_7/repeat_outer">' \
                '<input ' + appearance_attr + 'ref="/tmpkWhV2m/group_outer/' + field.name + '">' \
                '<label>' + field.label + '</label>' + hint_node + \
                '</input>' \
                '</repeat>'
            constraint_message_attr = 'constraintMsg="' + field.constraint_message + '" ' if field.constraint_message else ''
            required_attr = ' required="true()"' if field.is_required() else ''
            bind_node = '<bind ' + constraint_message_attr + 'nodeset="/tmpkWhV2m/group_outer/' + field.name + '"' + required_attr + ' type="string" />'
            instance_node = '<' + field.name + '>' + field.default + '</' + field.name + '>' if field.default else '<' + field.name + ' />'
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
                        <repeat_outer>\
                          {instance_node}</repeat_outer>\
                      </group_outer>\
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
                  <bind calculate="concat(''uuid:'', uuid())" nodeset="/tmpkWhV2m/meta/instanceID" readonly="true()" type="string" />\
                  {bind_node}</model>\
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
                  <group ref="/tmpRTha_7/repeat_outer">\
                    <label>Enter the details you wanna repeat</label>{input_node}\
                  </group>\
                </group>\
              </html:body>\
            </html:html>').format(**field_attrs))

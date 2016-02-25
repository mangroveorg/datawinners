import os
import unittest

from mangrove.form_model.field import Field, FieldSet
from mangrove.form_model.project import Project
from mangrove.form_model.tests.test_form_model_unit_tests import DatabaseManagerStub

from datawinners.blue.rules import EditLabelRule
from datawinners.blue.rules.rule import Rule

DIR = os.path.dirname(__file__)


class TestEditLabelRule(unittest.TestCase):

    def test_should_update_xform_with_label_change(self):
        edit_label_rule = EditLabelRule()
        self.maxDiff = None

        old_xform = self.get_xform("Name please", "text2")
        new_xform = self.get_xform("Full name please", "text2")
        old_questionnaire = Project(DatabaseManagerStub(), name="q1", fields=[
            FieldSet(code="group_outer", name="group_outer", label="Enter the outer group details", field_set=[
                Field(code="text2", name="text2", label="Name please", parent_field_code="group_outer", type="input")
            ])
        ], form_code="007")
        old_questionnaire.xform = old_xform
        new_questionnaire = Project(DatabaseManagerStub(), name="q1", fields=[
            FieldSet(code="group_outer", name="group_outer", label="Enter the outer group details", field_set=[
                Field(code="text2", name="text2", label="Full name please", parent_field_code="group_outer", type="input")
            ])
        ], form_code="007")
        new_questionnaire.xform = new_xform
        edit_label_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def get_xform(self, label, name):
        return ('<?xml version="1.0" encoding="utf-8"?><html:html xmlns="http://www.w3.org/2002/xforms" xmlns:html="http://www.w3.org/1999/xhtml">\
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
                        <' + name + ' />\
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
                  <bind nodeset="/tmpkWhV2m/group_outer/' + name + '" required="true()" type="string" />\
                  <bind calculate="concat(''uuid:'', uuid())" nodeset="/tmpkWhV2m/meta/instanceID" readonly="true()" type="string" />\
                </model>\
              </html:head>\
              <html:body>\
                <group ref="/tmpkWhV2m/group_outer">\
                  <label>Enter the outer group details</label>\
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
                  <input ref="/tmpkWhV2m/group_outer/' + name + '">\
                    <label>' + label + '</label>\
                  </input>\
                </group>\
              </html:body>\
            </html:html>')

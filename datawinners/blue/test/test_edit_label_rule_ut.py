import os
import unittest

from mangrove.datastore.documents import ProjectDocument
from mangrove.form_model.field import Field, FieldSet
from mangrove.form_model.project import Project
from mangrove.form_model.tests.test_form_model_unit_tests import DatabaseManagerStub

from datawinners.blue.rules import EditLabelRule

DIR = os.path.dirname(__file__)


class TestEditLabelRule(unittest.TestCase):

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

    def get_questionnaire(self, group_label="Enter the outer group details", group_name="group_outer",
                          field_label="Name please", field_name="text2"):
        doc = ProjectDocument()
        doc.xform = self.get_xform(field_label, field_name, group_label)
        questionnaire = Project.new_from_doc(DatabaseManagerStub(), doc)
        questionnaire.name = "q1"
        questionnaire.form_code = "007"
        questionnaire.fields.extend([
            FieldSet(code=group_name, name=group_name, label=group_label, field_set=[
                Field(code=field_name, name=field_name, label=field_label, parent_field_code=group_name)
            ])
        ])
        return questionnaire

    def get_xform(self, label, name, group_label):
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
                  <input ref="/tmpkWhV2m/group_outer/' + name + '">\
                    <label>' + label + '</label>\
                  </input>\
                </group>\
              </html:body>\
            </html:html>')

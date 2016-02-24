import os
import unittest

from mangrove.form_model.field import Field
from mangrove.form_model.project import Project
from mangrove.form_model.tests.test_form_model_unit_tests import DatabaseManagerStub

from datawinners.blue import rules
from datawinners.blue.rules import EditLabelRule

DIR = os.path.dirname(__file__)


class TestEditLabelRule(unittest.TestCase):

    def test_should_update_xform_with_label_change(self):
        edit_label_rule = EditLabelRule()
        self.maxDiff = None

        old_xform = self.get_xform("What is your name?", "f1")
        new_xform = self.get_xform("What is your new name?", "f1")
        old_questionnaire = Project(DatabaseManagerStub(), name="q1", fields=[Field(name="f1", label="What is your name?")], form_code="007")
        old_questionnaire.xform = old_xform
        new_questionnaire = Project(DatabaseManagerStub(), name="q1", fields=[Field(name="f1", label="What is your new name?")], form_code="007")
        new_questionnaire.xform = new_xform
        edit_label_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_not_update_xform_when_no_label_change(self):
        edit_label_rule = EditLabelRule()
        self.maxDiff = None

        old_xform = self.get_xform("What is your name?", "f1")
        new_xform = self.get_xform("What is your name?", "f2")
        old_questionnaire = Project(DatabaseManagerStub(), name="q1", fields=[Field(name="f1", label="What is your name?")], form_code="007")
        old_questionnaire.xform = old_xform
        new_questionnaire = Project(DatabaseManagerStub(), name="q1", fields=[Field(name="f2", label="What is your name?")], form_code="007")
        new_questionnaire.xform = new_xform
        edit_label_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertNotEqual(old_questionnaire.xform, new_questionnaire.xform)

    def get_xform(self, label, name):
        return ("""
                    <?xml version="1.0" encoding="utf-8"?>
                    <h:html xmlns="http://www.w3.org/2002/xforms" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:h="http://www.w3.org/1999/xhtml" xmlns:jr="http://openrosa.org/javarosa" xmlns:orx="http://openrosa.org/xforms" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                      <h:head>
                        <h:title>q1 What is your name?</h:title>
                        <model>
                          <instance>
                            <tmps8NKiE id="tmps8NKiE">
                              <""" + name + """/>
                              <meta>
                                <instanceID/>
                              </meta>
                            </tmps8NKiE>
                          </instance>
                          <bind nodeset="/tmps8NKiE/""" + name + """" required="true()" type="string"/>
                          <bind calculate="concat('uuid:', uuid())" nodeset="/tmps8NKiE/meta/instanceID" readonly="true()" type="string"/>
                        </model>
                      </h:head>
                      <h:body>
                        <input ref="/tmps8NKiE/""" + name + """">
                          <label>%s</label>
                        </input>
                      </h:body>
                    </h:html>
                """) % label

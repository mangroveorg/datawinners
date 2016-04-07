import os
import re
import unittest
import xml.etree.ElementTree as ET

from mangrove.datastore.documents import ProjectDocument
from mangrove.form_model.field import Field, FieldSet, SelectField
from mangrove.form_model.project import Project
from mangrove.form_model.tests.test_form_model_unit_tests import DatabaseManagerStub
from mangrove.form_model.xform import replace_node_name_with_xpath, Xform

from datawinners.blue.rules.add_rule import AddRule
from datawinners.blue.rules.bind_rule import EditConstraintMessageRule, EditRequiredRule, EditConstraintRule, \
    EditRelevantRule
from datawinners.blue.rules.choice_rule import ChoiceRule
from datawinners.blue.rules.instance_rule import EditDefaultRule
from datawinners.blue.rules.node_attribute_rule import EditAppearanceRule
from datawinners.blue.rules.node_rule import EditLabelRule, EditHintRule
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

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    hint="Enter your name")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    hint="Please enter your name")
        edit_hint_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_insert_hint_node_if_not_existing(self):
        edit_hint_rule = EditHintRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    hint="Please enter your name")
        edit_hint_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_remove_hint_node(self):
        edit_hint_rule = EditHintRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    hint="Please enter your name")
        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_hint_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_appearance_change(self):
        edit_appearance_rule = EditAppearanceRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    appearance="multiline")
        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_appearance_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    appearance="multiline")
        edit_appearance_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    appearance="sample")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    appearance="multiline")
        edit_appearance_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_relevant(self):
        edit_relevant_rule = EditRelevantRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    relevant="${number1}='1'")
        edit_relevant_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    relevant="${number1}='1'")
        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_relevant_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    relevant="${number1}='1'")

        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    relevant="${number1}='2'")
        edit_relevant_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)

        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_default_change(self):
        edit_default_rule = EditDefaultRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    default="18.31")
        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_default_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    default="18.31")
        edit_default_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    default="15")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    default="18.31")
        edit_default_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_required_to_optional_change(self):
        edit_default_rule = EditRequiredRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    required=True)

        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_default_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_optional_to_required_change(self):
        edit_default_rule = EditRequiredRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2")

        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    required=True)
        edit_default_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_constraint_message_change(self):
        edit_constraint_message_rule = EditConstraintMessageRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    constraint_message="Please enter your name")
        edit_constraint_message_rule.update_xform(old_questionnaire=old_questionnaire,
                                                  new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    constraint_message="Please enter your name")
        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_constraint_message_rule.update_xform(old_questionnaire=old_questionnaire,
                                                  new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    constraint_message="Please enter your name")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    constraint_message="Updated Please enter your name")
        edit_constraint_message_rule.update_xform(old_questionnaire=old_questionnaire,
                                                  new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_constraint_change(self):
        edit_constraint_rule = EditConstraintRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    xform_constraint=". > 10")
        edit_constraint_rule.update_xform(old_questionnaire=old_questionnaire,
                                                  new_questionnaire=new_questionnaire)
        self.assertEqual(ET.tostring(ET.fromstring(old_questionnaire.xform)), ET.tostring(ET.fromstring(new_questionnaire.xform)))

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    xform_constraint=". > 10")
        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_constraint_rule.update_xform(old_questionnaire=old_questionnaire,
                                                  new_questionnaire=new_questionnaire)
        self.assertEqual(ET.tostring(ET.fromstring(old_questionnaire.xform)), ET.tostring(ET.fromstring(new_questionnaire.xform)))

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    xform_constraint=". > 10")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    xform_constraint=". > 15")
        edit_constraint_rule.update_xform(old_questionnaire=old_questionnaire,
                                                  new_questionnaire=new_questionnaire)
        self.assertEqual(ET.tostring(ET.fromstring(old_questionnaire.xform)), ET.tostring(ET.fromstring(new_questionnaire.xform)))

        old_questionnaire = self._get_questionnaire(field_name="text2")

        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    xform_constraint="${number1}>1000")
        edit_constraint_rule.update_xform(old_questionnaire=old_questionnaire,
                                                  new_questionnaire=new_questionnaire)
        self.assertEqual(ET.tostring(ET.fromstring(old_questionnaire.xform)), ET.tostring(ET.fromstring(new_questionnaire.xform)))

    def test_should_update_xform_with_remove_field_change(self):
        remove_rule = RemoveRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire_with_field_removed()

        remove_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_add_field_change(self):
        add_rule = AddRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire_with_field_removed()
        new_questionnaire = self._get_questionnaire(field_name="text2")

        add_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_edit_choice_label(self):
        add_rule = ChoiceRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="hh_bottle_currency",
                                                    field_choices=[{"text": "Dollar", "val": "dollar"},
                                                                   {"text": "INR", "val": "rupee"}]
                                                    )
        new_questionnaire = self._get_questionnaire(field_name="hh_bottle_currency",
                                                    field_choices=[{"text": "USD", "val": "dollar"},
                                                                   {"text": "GBP", "val": "pound"}]
                                                    )

        add_rule.update_xform(old_questionnaire=old_questionnaire, new_questionnaire=new_questionnaire)
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def _get_questionnaire(self, group_label="Enter the outer group details", group_name="group_outer",
                           field_label="Name please", field_name="text2", hint=None, constraint_message=None,
                           appearance=None, default=None, required=False, xform_constraint=None, relevant=None,
                           field_choices=None):
        field = SelectField(field_name, field_name, field_label, field_choices) if field_choices is not None \
            else Field(code=field_name, name=field_name, label=field_label, parent_field_code=group_name, hint=hint,
                      constraint_message=constraint_message, appearance=appearance, default=default, required=required,
                      xform_constraint=xform_constraint, relevant=relevant)
        repeat = FieldSet(code="repeat_outer", name="repeat_outer", label="Enter the details you wanna repeat", field_set=[field])

        xform = self._build_xform(group_label, field)
        if field.relevant:
            xform = _replace_node_name_with_xpath(field.relevant, xform)
        elif field.xform_constraint:
            xform = _replace_node_name_with_xpath(field.xform_constraint, xform)

        doc = ProjectDocument()
        doc.xform = xform
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
        doc.xform = self._build_xform(group_label)
        questionnaire = Project.new_from_doc(DatabaseManagerStub(), doc)
        questionnaire.name = "q1"
        questionnaire.form_code = "007"
        questionnaire.fields.append(
            FieldSet(code=group_name, name=group_name, label=group_label, field_set=[repeat])
        )
        return questionnaire

    def _build_xform(self, group_label, field=None):
        bind_node = self._build_bind_node(field)
        instance_node = self._build_instance_node(field)

        if field and 'select' in field.type:
            node = self._build_select_node(field)
            file_name = os.path.join(DIR, "testdata/xform_xlsedit_select.xml")
        else:
            node = self._build_input_node(field)
            file_name = os.path.join(DIR, "testdata/xform_xlsedit_input.xml")

        field_attrs = {"group_label": group_label, "instance_node": instance_node, "bind_node": bind_node, "node": node}

        f = open(file_name, "r")
        return f.read().format(**field_attrs)

    def _build_instance_node(self, field):
        if field is None:
            return ""
        return '<%s>%s</%s>' % (field.name, field.default, field.name) if field.default else '<%s />' % field.name

    def _build_input_node(self, field):
        if field is None:
            return ""

        hint_node = '<hint>%s</hint>' % field.hint if field.hint else ''
        appearance_attr = 'appearance="%s" ' % field.appearance if field.appearance else ''
        return '<input %sref="/tmpkWhV2m/group_outer/repeat_outer/%s">\
            <label>%s</label>\
        %s</input>' % (appearance_attr, field.name, field.label, hint_node)

    def _build_select_node(self, field):
        if field is None:
            return ""

        items = []
        item_node = '<item><label>{text}</label><value>{val}</value></item>'

        for option in field.options:
            items.append(item_node.format(**option))

        return '<select1 ref="/tmpkWhV2m/hh_bottle_currency">\
            <label>Currency (specify one)</label>\
            %s</select1>' % ("".join(items))

    def _build_bind_node(self, field):
        if field is None:
            return ""

        relevant_attr = ' relevant="%s"' % field.relevant if field.relevant else ''
        constraint_attr = 'constraint="%s" ' % field.xform_constraint if field.xform_constraint else ''
        constraint_message_attr = 'constraintMsg="%s" ' % field.constraint_message if field.constraint_message else ''
        required_attr = ' required="true()"' if field.is_required() else ''
        bind_node = '<bind %s%snodeset="/tmpkWhV2m/group_outer/repeat_outer/%s"%s%s type="string" />' % \
                    (constraint_attr, constraint_message_attr, field.name, relevant_attr, required_attr)
        return bind_node


def _replace_node_name_with_xpath(value, xform_as_string):
    xform = Xform(xform_as_string)
    search_results = re.search('\$\{(.*?)\}', value)
    if search_results is None:
        return xform_as_string
    form_code = search_results.group(1)
    value_xpath = xform.get_bind_node_by_name(form_code).attrib['nodeset']
    return re.sub(r'(\$\{)' + form_code + '(\})', " " + value_xpath + " ", xform_as_string)


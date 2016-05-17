import os
import re
import unittest
import xml.etree.ElementTree as ET

from mangrove.datastore.documents import ProjectDocument
from mangrove.form_model.field import Field, FieldSet, SelectField
from mangrove.form_model.project import Project
from mangrove.form_model.tests.test_form_model_unit_tests import DatabaseManagerStub
from mangrove.form_model.xform import Xform

from datawinners.blue.rules.add_rule import AddRule
from datawinners.blue.rules.bind_rule import EditConstraintMessageRule, EditRequiredRule, EditConstraintRule, \
    EditRelevantRule
from datawinners.blue.rules.cascade_rule import CascadeRule
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
        edit_label_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_hint_change(self):
        edit_hint_rule = EditHintRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    hint="Enter your name")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    hint="Please enter your name")
        edit_hint_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_insert_hint_node_if_not_existing(self):
        edit_hint_rule = EditHintRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    hint="Please enter your name")
        edit_hint_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_remove_hint_node(self):
        edit_hint_rule = EditHintRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    hint="Please enter your name")
        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_hint_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_appearance_change(self):
        edit_appearance_rule = EditAppearanceRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    appearance="multiline")
        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_appearance_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    appearance="multiline")
        edit_appearance_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    appearance="sample")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    appearance="multiline")
        edit_appearance_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_relevant(self):
        edit_relevant_rule = EditRelevantRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    relevant="${number1}='1'")
        edit_relevant_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    relevant="${number1}='1'")
        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_relevant_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    relevant="${number1}='1'")

        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    relevant="${number1}='2'")
        edit_relevant_rule.update_xform(old_questionnaire, new_questionnaire, {})

        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_default_change(self):
        edit_default_rule = EditDefaultRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    default="18.31")
        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_default_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    default="18.31")
        edit_default_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    default="15")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    default="18.31")
        edit_default_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_required_to_optional_change(self):
        edit_default_rule = EditRequiredRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    required=True)

        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_default_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_optional_to_required_change(self):
        edit_default_rule = EditRequiredRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2")

        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    required=True)
        edit_default_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_constraint_message_change(self):
        edit_constraint_message_rule = EditConstraintMessageRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    constraint_message="Please enter your name")
        edit_constraint_message_rule.update_xform(old_questionnaire,
                                                  new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    constraint_message="Please enter your name")
        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_constraint_message_rule.update_xform(old_questionnaire,
                                                  new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    constraint_message="Please enter your name")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    constraint_message="Updated Please enter your name")
        edit_constraint_message_rule.update_xform(old_questionnaire,
                                                  new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_constraint_change(self):
        edit_constraint_rule = EditConstraintRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    xform_constraint=". > 10")
        edit_constraint_rule.update_xform(old_questionnaire,
                                                  new_questionnaire, {})
        self.assertEqual(ET.tostring(ET.fromstring(old_questionnaire.xform)), ET.tostring(ET.fromstring(new_questionnaire.xform)))

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    xform_constraint=". > 10")
        new_questionnaire = self._get_questionnaire(field_name="text2")
        edit_constraint_rule.update_xform(old_questionnaire,
                                                  new_questionnaire, {})
        self.assertEqual(ET.tostring(ET.fromstring(old_questionnaire.xform)), ET.tostring(ET.fromstring(new_questionnaire.xform)))

        old_questionnaire = self._get_questionnaire(field_name="text2",
                                                    xform_constraint=". > 10")
        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    xform_constraint=". > 15")
        edit_constraint_rule.update_xform(old_questionnaire,
                                                  new_questionnaire, {})
        self.assertEqual(ET.tostring(ET.fromstring(old_questionnaire.xform)), ET.tostring(ET.fromstring(new_questionnaire.xform)))

        old_questionnaire = self._get_questionnaire(field_name="text2")

        new_questionnaire = self._get_questionnaire(field_name="text2",
                                                    xform_constraint="${number1}>1000")
        edit_constraint_rule.update_xform(old_questionnaire,
                                                  new_questionnaire, {})
        self.assertEqual(ET.tostring(ET.fromstring(old_questionnaire.xform)), ET.tostring(ET.fromstring(new_questionnaire.xform)))

    def test_should_update_xform_with_remove_field_change(self):
        remove_rule = RemoveRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire(field_name="text2")
        new_questionnaire = self._get_questionnaire_with_field_removed()

        remove_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_remove_cascade_field_change(self):
        remove_rule = RemoveRule()
        self.maxDiff = None

        old_questionnaire = self._get_cascade_questionnaire(cascades={
            "respondent_district_counties": {
                "id": "counties",
                "options": [
                    {"text": "Bomi", "val": "bomi"},
                    {"text": "Bong", "val": "bong"}
                ]
            },
            "respondent_districts": {
                "id": "districts",
                "parent": "respondent_district_counties",
                "options": [
                    {"text": "Klay", "val": "klay", "counties": "bomi"},
                    {"text": "Klay 2", "val": "klay_2", "counties": "bong"}
                ]
            }
        })
        new_questionnaire = self._get_questionnaire_with_field_removed(field_type="cascade")

        remove_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(ET.tostring(ET.fromstring(old_questionnaire.xform)), ET.tostring(ET.fromstring(new_questionnaire.xform)))

    def test_should_update_xform_with_add_cascade_field_change(self):
        add_rule = AddRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire_with_field_removed(field_type="cascade")
        new_questionnaire = self._get_cascade_questionnaire(cascades={
            "respondent_district_counties": {
                "id": "counties",
                "options": [
                    {"text": "Bomi", "val": "bomi"},
                    {"text": "Bong", "val": "bong"}
                ]
            },
            "respondent_districts": {
                "id": "districts",
                "parent": "respondent_district_counties",
                "options": [
                    {"text": "Klay", "val": "klay", "counties": "bomi"},
                    {"text": "Klay 2", "val": "klay_2", "counties": "bong"}
                ]
            }
        })

        add_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_update_xform_with_add_field_change(self):
        add_rule = AddRule()
        self.maxDiff = None

        old_questionnaire = self._get_questionnaire_with_field_removed()
        new_questionnaire = self._get_questionnaire(field_name="text2")

        add_rule.update_xform(old_questionnaire, new_questionnaire, {})
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

        add_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def test_should_edit_cascade_choice(self):
        add_rule = CascadeRule()
        self.maxDiff = None

        old_questionnaire = self._get_cascade_questionnaire(cascades={
            "respondent_district_counties": {
                "id": "counties",
                "options": [
                    {"text": "Bomi", "val": "bomi"},
                    {"text": "Bong", "val": "bong"}
                ]
            },
            "respondent_districts": {
                "id": "districts",
                "parent": "respondent_district_counties",
                "options": [
                    {"text": "Klay", "val": "klay", "counties": "bomi"},
                    {"text": "Klay 2", "val": "klay_2", "counties": "bong"}
                ]
            }
        })
        new_questionnaire = self._get_cascade_questionnaire(cascades={
            "respondent_district_counties": {
                "id": "counties",
                "options": [
                    {"text": "Bomy", "val": "bomy"},
                    {"text": "Bong", "val": "bong"}
                ]
            },
            "respondent_districts": {
                "id": "districts",
                "parent": "respondent_district_counties",
                "options": [
                    {"text": "Klay", "val": "klay", "counties": "bomy"},
                    {"text": "Klay 3", "val": "klay_3", "counties": "bong"}
                ]
            }
        })

        add_rule.update_xform(old_questionnaire, new_questionnaire, {})
        self.assertEqual(old_questionnaire.xform, new_questionnaire.xform)

    def _get_cascade_questionnaire(self, cascades):
        fields = []
        for cascade in cascades:
            fields.append(SelectField(cascade, cascade, "Please select", cascades[cascade], is_cascade=True))

        doc = ProjectDocument()
        doc.xform = self._build_xform(fields=fields, field_type="cascade", cascades=cascades)
        questionnaire = Project.new_from_doc(DatabaseManagerStub(), doc)
        questionnaire.name = "q1"
        questionnaire.form_code = "007"
        questionnaire.fields.append(
            FieldSet(code="group_outer", name="group_outer", label="Enter the outer group details", field_set=[
                FieldSet(code="repeat_outer",
                    name="repeat_outer",
                    label="Enter the details you wanna repeat",
                    field_set=fields)
            ])
        )
        return questionnaire

    def _get_questionnaire(self, group_label="Enter the outer group details", group_name="group_outer",
                           field_label="Name please", field_name="text2", hint=None, constraint_message=None,
                           appearance=None, default=None, required=False, xform_constraint=None, relevant=None,
                           field_choices=None):
        field = SelectField(field_name, field_name, field_label, field_choices) if field_choices is not None \
            else Field(code=field_name, name=field_name, label=field_label, parent_field_code=group_name, hint=hint,
                      constraint_message=constraint_message, appearance=appearance, default=default, required=required,
                      xform_constraint=xform_constraint, relevant=relevant)
        repeat = FieldSet(code="repeat_outer", name="repeat_outer", label="Enter the details you wanna repeat", field_set=[field])

        xform = self._build_xform(group_label=group_label, fields=[field], field_type=field.type)
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
                                              group_name="group_outer", field_type=None):
        repeat = FieldSet(code="repeat_outer", name="repeat_outer", label="Enter the details you wanna repeat", field_set=[])
        doc = ProjectDocument()
        doc.xform = self._build_xform(group_label=group_label, field_type=field_type)
        questionnaire = Project.new_from_doc(DatabaseManagerStub(), doc)
        questionnaire.name = "q1"
        questionnaire.form_code = "007"
        questionnaire.fields.append(
            FieldSet(code=group_name, name=group_name, label=group_label, field_set=[repeat])
        )
        return questionnaire

    def _build_xform(self, group_label=None, fields=None, field_type=None, cascades=None):
        field_attrs = {"group_label": "" if group_label is None else group_label, "translation": "",
                       "instance_node_0": "", "bind_node_0": "", "node_0": "", "cascade_instance_node_0": "",
                       "instance_node_1": "", "bind_node_1": "", "node_1": "", "cascade_instance_node_1": "",}
        if fields:
            for index, field in enumerate(fields):
                field_attrs["instance_node_%s" % index] = self._build_instance_node(field)
                field_attrs["bind_node_%s" % index] = self._build_bind_node(field)
                field_attrs["node_%s" % index] = self._build_node(field, field_type, cascades=cascades)
                field_attrs["cascade_instance_node_%s" % index] = self._build_cascade_instance_node(field, cascades)
            field_attrs["translation"] = self._build_translation_node(cascades)

        return self.xform_template(field_type).format(**field_attrs)

    def xform_template(self, field_type):
        if field_type and 'select' in field_type:
            file_name = os.path.join(DIR, "testdata/xform_xlsedit_select.xml")
        elif field_type and 'cascade' in field_type:
            file_name = os.path.join(DIR, "testdata/xform_xlsedit_cascade.xml")
        else:
            file_name = os.path.join(DIR, "testdata/xform_xlsedit_input.xml")
        f = open(file_name, "r")
        return f.read()

    def _build_node(self, field, field_type, cascades=None):
        node = self._build_input_node(field)
        if 'select' in field_type:
            node = self._build_select_node(field)
        elif 'cascade' in field_type:
            node = self._build_cascade_node(field, cascades)
        return node

    def _build_instance_node(self, field):
        return '<%s>%s</%s>' % (field.name, field.default, field.name) if field.default else '<%s />' % field.name

    def _build_input_node(self, field):
        hint_node = '<hint>%s</hint>' % field.hint if field.hint else ''
        appearance_attr = 'appearance="%s" ' % field.appearance if field.appearance else ''
        return '<input %sref="/tmpkWhV2m/group_outer/repeat_outer/%s">\
            <label>%s</label>\
        %s</input>' % (appearance_attr, field.name, field.label, hint_node)

    def _build_select_node(self, field):
        items = []
        item_node = '<item><label>{text}</label><value>{val}</value></item>'

        for option in field.options:
            items.append(item_node.format(**option))

        return '<select1 ref="/tmpkWhV2m/group_outer/repeat_outer/%s">\
            <label>Currency (specify one)</label>\
            %s</select1>' % (field.name, "".join(items))

    def _build_cascade_node(self, field, cascades):
        current = cascades[field.name]
        parent = cascades.get(current.get("parent"))
        parent_ref = "[%s= /tmpkWhV2m/%s ]" % (parent["id"], (current.get("parent"))) if parent is not None else ""
        return '<select1 ref="/tmpkWhV2m/group_outer/repeat_outer/%s">\
            <label>%s</label>\
            <itemset nodeset="instance(\'%s\')/root/item%s">\
                <value ref="name" />\
                <label ref="jr:itext(itextId)" />\
            </itemset>\
        </select1>' % (field.name, field.label, current["id"], parent_ref)

    def _build_bind_node(self, field):
        relevant_attr = ' relevant="%s"' % field.relevant if field.relevant else ''
        constraint_attr = 'constraint="%s" ' % field.xform_constraint if field.xform_constraint else ''
        constraint_message_attr = 'constraintMsg="%s" ' % field.constraint_message if field.constraint_message else ''
        required_attr = ' required="true()"' if field.is_required() else ''
        bind_node = '<bind %s%snodeset="/tmpkWhV2m/group_outer/repeat_outer/%s"%s%s type="string" />' % \
                    (constraint_attr, constraint_message_attr, field.name, relevant_attr, required_attr)
        return bind_node

    def _build_translation_node(self, cascades):
        if cascades is None:
            return ""
        translation_str = ""
        for cascade in cascades:
            options = cascades[cascade]['options']
            for index, option in enumerate(options):
                translation_str += '<text id="static_instance-%s-%s">\
                                        <value>%s</value>\
                                    </text>' % (cascades[cascade]['id'], index, option['text'])
        return translation_str

    def _build_cascade_instance_node(self, field, cascades):
        if cascades is None:
            return ""
        cascade = cascades[field.name]
        instance_start_str = '<instance id="%s"><root>' % cascade['id']
        instance_end_str = '</root></instance>'
        instance_items_str = ""
        for index, option in enumerate(cascade['options']):
            parents = ""
            for key in option:
                if key not in ["text", "val"]:
                    parents += "<%s>%s</%s>" % (key, option[key] , key)
            instance_items_str += "<item>\
                                        <itextId>\
                                            static_instance-%s-%s\
                                        </itextId>\
                                        <name>%s</name>\
                                        %s\
                                    </item>" % (cascade['id'], index, option['val'], parents)
        return instance_start_str + instance_items_str + instance_end_str

def _replace_node_name_with_xpath(value, xform_as_string):
    xform = Xform(xform_as_string)
    search_results = re.search('\$\{(.*?)\}', value)
    if search_results is None:
        return xform_as_string
    form_code = search_results.group(1)
    value_xpath = xform.get_bind_node_by_name(form_code).attrib['nodeset']
    return re.sub(r'(\$\{)' + form_code + '(\})', " " + value_xpath + " ", xform_as_string)


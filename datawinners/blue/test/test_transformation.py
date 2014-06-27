from StringIO import StringIO
import os
import unittest

from lxml import etree
from nose.plugins.attrib import attr

from datawinners.blue.xform_bridge import XFormTransformer


DIR = os.path.dirname(__file__)


class TestTransformations(unittest.TestCase):
    def setUp(self):
        self.test_data = os.path.join(DIR, 'testdata')
        self.REPEAT_XFORM = os.path.join(self.test_data, 'repeat-xform.xml')
        self.xls_folder = os.path.join(DIR, '../xsl')
        self.HTML_FORM = os.path.join(self.xls_folder, 'openrosa2html5form_php5.xsl')
        self.XML_MODEL = os.path.join(self.xls_folder, 'openrosa2xmlmodel.xsl')

    @attr('dcs')
    def test_transformation(self):
        transformed_xml = XFormTransformer(open(self.REPEAT_XFORM, 'r').read()).transform()
        expected_transformed_xml = open(os.path.join(self.test_data, 'xform_transformed.xml'), 'r').read()

        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(transformed_xml, parser)
        expected_tree = etree.fromstring(expected_transformed_xml, parser)

        self.assertEqual(etree.tostring(expected_tree), etree.tostring(tree))
        #print etree.tostring(expected_tree) #add -s config param

        # f=open(os.path.join(self.test_data,'inter.xml'), 'w')
        # f.write(XFormTransformer(open(self.REPEAT_XFORM, 'r').read()).transform())
        # f.close()

    def test_sample(self):
        xslt_root = etree.XML('''
        <xsl:stylesheet version="1.0"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:template match="/">
                <foo><xsl:value-of select="/a/b/text()" /></foo>
            </xsl:template>
        </xsl:stylesheet>''')
        transform = etree.XSLT(xslt_root)
        f = StringIO('<a><b>Text</b></a>')
        doc = etree.parse(f)
        result_tree = transform(doc)
        print etree.tostring(result_tree)

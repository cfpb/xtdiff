# -*- coding: utf-8 -*-

from unittest import TestCase, skip

import lxml.etree as etree

from ..xsl import xsldiff


class XDiffXSLTestCase(TestCase):

    def test_toxsl_insert(self):
        root_one = etree.fromstring("<root></root>")
        root_two = etree.fromstring("<root><first>A child Node</first></root>")
        xsl = xsldiff(root_one, root_two)
        transform = etree.XSLT(xsl)
        result = transform(root_one)
        self.assertEqual(etree.tostring(result),
                         etree.tostring(root_two))

    def test_toxsl_update_text(self):
        root_one = etree.fromstring("<root><first>Some text</first></root>")
        root_two = etree.fromstring("<root><first>Some text more</first></root>")

        xsl = xsldiff(root_one, root_two)
        transform = etree.XSLT(xsl)
        result = transform(root_one)

        self.assertEqual(etree.tostring(result),
                         etree.tostring(root_two))

    @skip
    # XXX: We don't handle attribute changes well at all yet.
    def test_toxsl_update_attributes(self):
        root_one = etree.fromstring('<root><first attr="old">Some text</first></root>')
        root_two = etree.fromstring(
            '<root><first attr="new" and="more">Some text</first></root>')

        xsl = xsldiff(root_one, root_two)
        transform = etree.XSLT(xsl)
        result = transform(root_one)

        self.assertEqual(etree.tostring(result),
                         etree.tostring(root_two))

    @skip
    # XXX: We don't handle tail text changes well at all yet.
    def test_toxsl_update_tail(self):
        root_one = etree.fromstring("<root><first>Some text</first> more</root>")
        root_two = etree.fromstring("<root><first>Some text</first> less</root>")

        xsl = xsldiff(root_one, root_two)
        print(etree.tostring(xsl))

        transform = etree.XSLT(xsl)
        result = transform(root_one)
        print(etree.tostring(result))

        self.assertEqual(etree.tostring(result),
                         etree.tostring(root_two))

    def test_toxsl_move(self):
        root_one = etree.fromstring("<root><foo>bar</foo><foo>first</foo></root>")
        root_two = etree.fromstring("<root><foo>first</foo><foo>bar</foo></root>")

        xsl = xsldiff(root_one, root_two)
        transform = etree.XSLT(xsl)
        result = transform(root_one)

        self.assertEqual(etree.tostring(result),
                         etree.tostring(root_two))

    def test_toxsl_delete(self):
        root_one = etree.fromstring("<root><foo/></root>")
        root_two = etree.fromstring("<root></root>")

        xsl = xsldiff(root_one, root_two)
        transform = etree.XSLT(xsl)
        result = transform(root_one)

        self.assertEqual(etree.tostring(result),
                         etree.tostring(root_two))

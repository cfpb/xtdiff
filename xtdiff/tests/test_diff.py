# -*- coding: utf-8 -*-

from unittest import TestCase

import lxml.etree as etree

from ..diff import (INSERT, UPDATE, MOVE, DELETE, THRESHOLD,
                    Match, simplematch as match, lcs,
                    common_descendents, compare, equal_match,
                    matching_partner, diff,
                    transform)


class XDiffTestCase(TestCase):

    def test_common_descendents_almost(self):
        root_one = etree.fromstring('<foo><bar attr="omg"/><feh>woot</feh></foo>')
        root_two = etree.fromstring('<foo><feh>woot</feh></foo>')
        self.assertEqual(0.5, common_descendents(root_one, root_two))

    def test_common_descendents_one(self):
        root_one = etree.fromstring('<foo><bar attr="omg"/><feh>woot</feh></foo>')
        root_two = etree.fromstring('<foo><bar attr="omg"/><feh>woot</feh></foo>')
        self.assertEqual(1.0, common_descendents(root_one, root_two))

    def test_compare(self):
        # Straight compare
        root_one = etree.fromstring('<foo>woot</foo>')
        root_two = etree.fromstring('<foo>woot</foo>')
        self.assertEqual(compare(root_one, root_two), 2)

    def test_compare_mostly(self):
        # Mostly matching
        root_one = etree.fromstring('<foo>woot</foo>')
        root_two = etree.fromstring('<foo>woohoot</foo>')
        self.assertTrue(compare(root_one, root_two) > THRESHOLD * 2)

    def test_compare_attr(self):
        # Attributes match, text mostly matches. Should be the same as
        # above.
        root_one = etree.fromstring('<foo one="two" two="one">woot</foo>')
        root_two = etree.fromstring('<foo two="one" one="two">woohoot</foo>')
        self.assertTrue(compare(root_one, root_two) > THRESHOLD * 2)

    def test_compare_attr_inequality(self):
        # Attribute inequality, should be quite a bit less than above
        root_one = etree.fromstring('<foo one="two" two="one">woot</foo>')
        root_two = etree.fromstring('<foo two="three" one="two">woohoot</foo>')
        self.assertTrue(compare(root_one, root_two) < THRESHOLD * 2)

    def test_equal_match_mostly(self):
        # Mostly true — this matches our threshold.
        root_one = etree.fromstring('<foo>woot</foo>')
        root_two = etree.fromstring('<foo>woohoot</foo>')
        self.assertTrue(equal_match(root_one, root_two))

    def test_equal_match_not(self):
        # This should not match our threshold
        root_one = etree.fromstring('<foo>asdfghjkl</foo>')
        root_two = etree.fromstring('<foo>zxcvbnm</foo>')
        self.assertFalse(equal_match(root_one, root_two))

    def test_equal_match(self):
        # Straight up true
        root_one = etree.fromstring('<foo>woot</foo>')
        root_two = etree.fromstring('<foo>woot</foo>')
        self.assertTrue(equal_match(root_one, root_two))

    def test_equal_match_attr(self):
        # Attribute truth — should meet the threshold
        root_one = etree.fromstring('<foo one="two" two="one">woot</foo>')
        root_two = etree.fromstring('<foo two="one" one="two">woohoot</foo>')
        self.assertTrue(equal_match(root_one, root_two))

    def test_equal_ids(self):
        # Should be equal regardless of difference.
        root_one = etree.fromstring('<foo id="foo" one="two">woot</foo>')
        root_two = etree.fromstring('<foo id="foo" bar="bar">asdfgh</foo>')
        self.assertTrue(equal_match(root_one, root_two))

    def test_lcs(self):
        xs = 'HUMAN'
        ys = 'CHIMPANZEE'
        self.assertEqual(lcs(xs, ys, lambda x, y: x == y),
                         {('A', 'A'), ('N', 'N'), ('M', 'M'), ('H', 'H')})

    def test_matching_partner(self):
        matches = {Match('a', 'b'), Match('c', 'd'), }
        self.assertEqual(matching_partner(matches, 'a'), 'b')
        self.assertEqual(matching_partner(matches, 'b'), 'a')
        self.assertEqual(matching_partner(matches, 'd'), 'c')

    def test_match_direct(self):
        # Direct match
        root_one = etree.fromstring("<root><first><second>Child Node</second></first></root>")
        root_two = etree.fromstring("<root><first><second>Child Node</second></first></root>")
        matches = match(root_one, root_two)
        self.assertEqual(3, len(matches))

    def test_match_below_threshold(self):
        # Should won't meet the threshold
        root_one = etree.fromstring("<root><first><second>asdfghjkl</second></first></root>")
        root_two = etree.fromstring("<root><first><second>zxcvbnm</second></first></root>")
        matches = match(root_one, root_two)
        self.assertEqual(0, len(matches))

    def test_match_bottom_two(self):
        # This should still match the bottom two nodes
        root_one = etree.fromstring("<root><first><second><third>Child Node</third></second></first></root>")
        root_two = etree.fromstring("<root><second><third>Child Node</third></second></root>")
        matches = match(root_one, root_two)
        self.assertEqual(2, len(matches))

    def test_match_nothing(self):
        root_one = etree.fromstring("<root><first><second>asdfghjkl</second></first></root>")
        root_two = etree.fromstring("<root><first><second><fourth>zxcvbnm</fourth></second></first></root>")
        matches = match(root_one, root_two)
        self.assertEqual(0, len(matches))

    def test_diff_nodiff(self):
        # These are the same, the edit script should be no different.
        root_one = etree.fromstring("<root><first><second>Child Node</second></first></root>")
        root_two = etree.fromstring("<root><first><second>Child Node</second></first></root>")
        script = diff(root_one, root_two)
        self.assertEqual(0, len(script))

    def test_diff_update(self):
        root_one = etree.fromstring("<root><first>Some text</first></root>")
        root_two = etree.fromstring("<root><first>Some text more</first></root>")
        script = diff(root_one, root_two)
        self.assertEqual(1, len(script))
        self.assertEqual(
            {UPDATE(path='/root/first', text='Some text more',
                    tail=None, attrib=frozenset()), },
            script)

    def test_diff_insert(self):
        root_one = etree.fromstring("<root></root>")
        root_two = etree.fromstring("<root><first>A child Node</first></root>")
        script = diff(root_one, root_two)
        self.assertEqual(1, len(script))
        self.assertEqual(
            {INSERT(node=b'<first>A child Node</first>',
                    parent='/root', index=0)},
            script)

    def test_diff_move(self):
        root_one = etree.fromstring("<root><foo>bar</foo><foo>first</foo></root>")
        root_two = etree.fromstring("<root><foo>first</foo><foo>bar</foo></root>")
        script = diff(root_one, root_two)
        self.assertEqual(1, len(script))
        self.assertEqual(
            {MOVE(path='/root/foo[2]', parent='/root', index=0)},
            script)

    def test_diff_delete(self):
        root_one = etree.fromstring("<root><foo/></root>")
        root_two = etree.fromstring("<root></root>")
        script = diff(root_one, root_two)
        self.assertEqual(1, len(script))
        self.assertEqual({DELETE(path='/root/foo')}, script)

    def test_transform_update(self):
        root_one = etree.fromstring("<root><first>Some text</first></root>")
        root_two = etree.fromstring("<root><first>Some text more</first></root>")
        script = {
            UPDATE(path='/root/first', text='Some text more', tail=None,
                   attrib=frozenset())
        }
        result = transform(root_one, script)
        self.assertEqual(etree.tostring(result),
                         etree.tostring(root_two))

    def test_transform_insert(self):
        root_one = etree.fromstring("<root></root>")
        root_two = etree.fromstring("<root><first>A child Node</first></root>")
        script = {
            INSERT(node=b'<first>A child Node</first>', parent='/root',
                   index=0)
        }
        result = transform(root_one, script)
        self.assertEqual(etree.tostring(result),
                         etree.tostring(root_two))

    def test_transform_move(self):
        root_one = etree.fromstring("<root><foo>bar</foo><foo>first</foo></root>")
        root_two = etree.fromstring("<root><foo>first</foo><foo>bar</foo></root>")
        script = {
            MOVE(path='/root/foo[2]', parent='/root', index=0),
        }
        result = transform(root_one, script)
        self.assertEqual(etree.tostring(result),
                         etree.tostring(root_two))

    def test_transform_delete(self):
        root_one = etree.fromstring("<root><foo/></root>")
        root_two = etree.fromstring("<root></root>")
        script = {DELETE(path='/root/foo')}
        result = transform(root_one, script)
        self.assertEqual(etree.tostring(result),
                         etree.tostring(root_two))

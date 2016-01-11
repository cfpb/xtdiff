# -*- coding: utf-8 -*-
"""
Python xtdiff

This implements "Change detection in hierarchically structured
information", by Sudarshan S. Chawathe, Anand Rajaraman, Hector
Garcia-Molina, and Jennifer Widom.

Chawathe, Sudarshan S., Anand Rajaraman, Hector Garcia-Molina, and
Jennifer Widom. "Change detection in hierarchically structured
information." In ACM SIGMOD Record, vol. 25, no. 2, pp. 493-504. ACM,
1996.
"""

from __future__ import unicode_literals

import re

from lxml import etree

from .diff import INSERT, UPDATE, MOVE, DELETE
from .diff import simplematch, THRESHOLD
from .diff import diff


XSL_NAMESPACE = 'http://www.w3.org/1999/XSL/Transform'
XSL = '{%s}' % XSL_NAMESPACE
NSMAP = {'xsl': XSL_NAMESPACE}


def insert(action, xsl):
    """
    <xsl:template match="/parent">
        <xsl:copy>
            <xsl:copy-of select="*[position() < action.index"/>
            action.node
            <xsl:copy-of select="*[position() >= action.index"/>
        </xsl:copy>
    </xsl:template>
    """
    insert = etree.Element(XSL + 'template', nsmap=NSMAP)
    insert.set('match', action.parent)
    copy = etree.SubElement(insert, XSL + 'copy', nsmap=NSMAP)

    # Select and keep all the elements that preceed the index where
    # we're inserting.
    preceeding_copy_of = etree.SubElement(copy,
                                          XSL + 'copy-of',
                                          nsmap=NSMAP)
    preceeding_copy_of.set('select',
                           '*[position() < {}]'.format(str(action.index)))

    # Insert the new element
    copy.append(etree.fromstring(action.node))

    # Select and keep all subsequent elements.
    succeeding_copy_of = etree.SubElement(copy,
                                          XSL + 'copy-of',
                                          nsmap=NSMAP)
    succeeding_copy_of.set('select',
                           '*[position() >= {}]'.format(str(action.index)))

    xsl.append(insert)


def update(action, xsl):
    """
    <xsl:template match="/parent">
        <xsl:copy>
            <xsl:copy-of select="*[position() < action.index"/>
            action.node
            <xsl:copy-of select="*[position() >= action.index"/>
        </xsl:copy>
    </xsl:template>
    """
    update = etree.Element(XSL + 'template', nsmap=NSMAP)
    update.set('match', action.path + '/text()')

    # Update text
    text = etree.SubElement(update, XSL + 'text', nsmap=NSMAP)
    text.text = action.text

    # Update attributes
    # XXX: This is not implemented yet because the matching/script
    # code doesn't generate an UDPATE for attribute changes right
    # now.

    xsl.append(update)

    # Update tail
    # XXX: This is not implemented yet because tail
    # matching/actions/etc are just fubar.
    # if action.tail:
    #     update_tail = etree.Element(XSL + 'template', nsmap=NSMAP)
    #     update_tail.set('match', action.path + '/following-sibling::text()')
    #     text = etree.SubElement(update_text, XSL + 'text',
    #             nsmap=NSMAP)
    #     text.text = action.tail
    #     xsl.append(update_tail)


def move(action, xsl):
    """
    <xsl:template match="/node/path"></xsl:template>
    <xsl:template match="/new/parent">
        <xsl:copy>
            <xsl:copy-of select="*[position() < action.index"/>
            <xsp:copy-of select="/node/path"/>
            <xsl:copy-of select="*[position() >= action.index"/>
        </xsl:copy>
    </xsl:template>
    """
    # To move a node basically amounts to a combination of insert
    # and delete. It is inserted into the parent node and deleted
    # from its original location.

    # Find out if the parent already has a template match. If so, we'll
    # append to that.
    parent_matches = xsl.xpath('//*[@match="{}"]'.format(action.parent))
    if len(parent_matches) > 0:
        parent = parent_matches[0]
    else:
        parent = etree.SubElement(xsl, XSL + 'template', nsmap=NSMAP)

    parent.set('match', action.parent)
    insert_copy = etree.SubElement(parent, XSL + 'copy', nsmap=NSMAP)

    # Extract the original position
    # XXX: Is there a way to make this feel less fragile while not
    # cluttering up our edit script?
    index = re.match(r'.*\[([(0-9)+])\]', action.path).groups()[0]

    # Select and keep all the elements that preceed the index where
    # we're inserting.
    prec_copy_of = etree.SubElement(insert_copy,
                                    XSL + 'copy-of',
                                    nsmap=NSMAP)
    prec_copy_of.set('select',
                     '*[position() < {} and position() != {}]'.format(
                         str(action.index + 1), str(index)))

    # Insert the new element
    insert_copy_of = etree.SubElement(insert_copy,
                                      XSL + 'copy-of',
                                      nsmap=NSMAP)
    insert_copy_of.set('select', action.path)

    # Select and keep all subsequent elements.
    succ_copy_of = etree.SubElement(insert_copy,
                                    XSL + 'copy-of',
                                    nsmap=NSMAP)
    succ_copy_of.set('select',
                     '*[position() >= {} and  position() != {}]'.format(
                         str(action.index + 1), str(index)))

    delete = etree.Element(XSL + 'template', nsmap=NSMAP)
    delete.set('match', action.path)
    xsl.append(delete)


def delete(action, xsl):
    """
    <xsl:template match="/node/path"></xsl:template>
    """
    delete = etree.Element(XSL + 'template', nsmap=NSMAP)
    delete.set('match', action.path)
    xsl.append(delete)


def toxsl(script, insert=insert, update=update, move=move,
          delete=delete):
    ''' Convert the given edit script to an XSL stylesheet.  '''

    # Create the XSL stylesheet
    xsl = etree.Element(XSL + 'stylesheet', nsmap=NSMAP)

    # Create the identity transformation
    match_all = etree.SubElement(xsl, XSL + 'template', nsmap=NSMAP)
    match_all.set('match', '@* | node()')
    match_all_copy = etree.SubElement(match_all, XSL + 'copy', nsmap=NSMAP)
    match_all_apply = etree.SubElement(match_all_copy,
                                       XSL + 'apply-templates',
                                       nsmap=NSMAP)
    match_all_apply.set('select', '@* | node()')
    match_all_apply.set('name', 'identity')

    # Create transformations for each action
    for action in script:
        if type(action) == INSERT:
            insert(action, xsl)

        elif type(action) == UPDATE:
            update(action, xsl)

        elif type(action) == MOVE:
            move(action, xsl)

        elif type(action) == DELETE:
            delete(action, xsl)

    return xsl


def xsldiff(left_tree, right_tree, match=simplematch,
            match_threshold=THRESHOLD):
    """ Simple wrapper around toxsl(diff()) """

    return toxsl(diff(left_tree, right_tree, match=match,
                      match_threshold=match_threshold))

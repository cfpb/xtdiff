# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from collections import namedtuple
from copy import deepcopy
from difflib import SequenceMatcher
from collections import MutableSet

from lxml import etree


# The default equality threshold
THRESHOLD = 0.8

# This is a simple definition of our possible edit actions
INSERT = namedtuple('INSERT', ['node', 'parent', 'index'])
DELETE = namedtuple('DELETE', ['path'])
UPDATE = namedtuple('UPDATE', ['path', 'text', 'tail', 'attrib'])
MOVE = namedtuple('MOVE', ['path', 'parent', 'index'])

# A simple Match between two elements, a and b.
Match = namedtuple('Match', ['a', 'b'])


# http://code.activestate.com/recipes/576694-orderedset/
class OrderedSet(MutableSet):

    def __init__(self, iterable=None):
        self.end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def update(self, sequence):
        try:
            for item in sequence:
                self.add(item)
        except TypeError:
            raise ValueError('Expected an iterable, got %s' % type(sequence))
        return self

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)


def getpath(node):
    """ Return the XPath for the given node. This wraps a couple of lxml
        functions for convenience """
    return node.getroottree().getpath(node)


def compare(left_node, right_node):
    """
        Evaluate how different left_node's text, tail, and attributes
        are from right_node's text, tail, and attributes. The nodes
        should probably be leaf nodes, but this is enforced.

        This will return a number in the range [0,2]
    """

    # Just use difflib.SequenceMatcher's ratio for this.
    ratio = 0

    # Matching attributes add a lot of weight to matching elements
    if left_node.attrib == right_node.attrib:
        ratio += 1

    if left_node.text is not None and right_node.text is not None:
        text_matcher = SequenceMatcher(a=left_node.text, b=right_node.text)
        ratio += text_matcher.ratio()
    elif left_node.text is None and right_node.text is None:
        # Both are None
        ratio += 1

    # XXX: Tail text is problematic. We need to handle it better.
    # if left_node.tail is not None and right_node.tail is not None:
    #     tail_matcher = SequenceMatcher(a=left_node.tail, b=right_node.tail)
    #     ratio += tail_matcher.ratio()
    # elif left_node.tail is None and right_node.tail is None:
    #     # Both are None
    #     ratio += 1
    #
    # return (ratio * 2 / 3)

    return ratio


def common_descendents(left_node, right_node, threshold=THRESHOLD):
    """ Return the a ratio of common descendents between the two nodes
        over the maximum number of descendents between either. """

    count = 0.0

    # Text nodes can't have descendents, so there's no commonality
    if hasattr(left_node, 'is_text') and left_node.is_text or \
            hasattr(right_node, 'is_text') and right_node.is_text:
        return count

    # Cycle over and count children
    left_descendents = left_node.xpath('.//*')
    right_descendents = right_node.xpath('.//*')
    for left_child in left_descendents:
        for right_child in right_descendents:
            if compare(left_child, right_child) >= (threshold * 2):
                count += 1

    max_descendents = max(len(left_descendents), len(right_descendents))
    if max_descendents > 0:
        return count / max_descendents
    return 0.0


def equal_match(left_node, right_node, threshold=THRESHOLD):
    """ Rough equality matching for our matching algorithm. """

    # If their tags aren't equal, the nodes aren't equal.
    if left_node.tag != right_node.tag:
        return False

    # If there's a matching id between the two elements, they are
    # automatically equal.
    if left_node.get('id') is not None and \
            right_node.get('id') is not None and \
            left_node.get('id') == right_node.get('id'):
        return True

    # Compare leaf nodes
    if len(left_node.getchildren()) == 0 and \
            len(right_node.getchildren()) == 0:
        if compare(left_node, right_node) >= (threshold * 2):
            return True

    # Compare internal nodes
    else:
        # XXX: This causes an insert on otherwise good nodes that simply
        # have lost all their children...
        if common_descendents(left_node, right_node,
                              threshold=threshold) >= threshold:
            return True

    # If nothing else is true, then we need to return false
    return False


def lcs(x_sequence, y_sequence, equal_func):
    """ Myers's Longest Common Subsequence """

    if not len(x_sequence) or not len(y_sequence):
        return OrderedSet()

    # Get the first item of each list and the remainder of each list as
    # a list.

    # NOTE: To support 2.7 we can't use Python3's very nice unpacking
    # syntax. Leaving it here for future, because the old way is ugly.
    # x, *x_remaining = x_sequence
    # y, *y_remaining = y_sequence
    x, x_remaining = x_sequence[0], x_sequence[1:]
    y, y_remaining = y_sequence[0], y_sequence[1:]

    if equal_func(x, y):
        # If x and y are equal according to the given equal funciton,
        # return them as common and recurse through the rest
        sequence = set([(x, y), ])
        sequence.update(lcs(x_remaining, y_remaining, equal_func))
        return sequence

    else:
        # Otherwise return the largest of the matches of either the
        # remainder or xs with ys or the remainder of ys with xs
        return max(lcs(x_sequence, y_remaining, equal_func),
                   lcs(x_remaining, y_sequence, equal_func),
                   key=len)


def simplematch(left_root, right_root, threshold=THRESHOLD):
    """ Return a matching of left and right nodes. This is based on the
        simple matching algorithm. """

    matches = OrderedSet()

    # If their path isn't the same at the root, there are no
    # matches
    if getpath(left_root) != getpath(right_root):
        return matches

    # Get leaf nodes in the left root
    left_leaves = left_root.xpath('//*[not(child::*)]')
    right_leaves = right_root.xpath('//*[not(child::*)]')

    while len(left_leaves) > 0 and len(right_leaves) > 0:
        for left_node in left_leaves:
            for right_node in right_leaves:
                if equal_match(left_node, right_node, threshold=threshold):
                    matches.add(Match(left_node, right_node))

        # Parent nodes of previous nodes
        left_leaves = [n.getparent() for n in left_leaves
                       if n.getparent() is not None]
        right_leaves = [n.getparent() for n in right_leaves
                        if n.getparent() is not None]

    return matches


def fastmatch(left_root, right_root, threshold=THRESHOLD):
    """ Return a minimum-cost matching of left and right roots. Based on
        the fast match algorithm. """

    matches = OrderedSet()

    # If their path isn't the same at the root, there are no
    # matches
    if getpath(left_root) != getpath(right_root):
        return matches

    # Get leaf nodes in the left root
    left_leaves = left_root.xpath('//*[not(child::*)]')

    # Get a list of all nodes
    left_nodes = left_root.xpath('//*')
    right_nodes = right_root.xpath('//*')

    # Get leaf node tags in the left root. We'll proceed from the
    # bottom of the root by tags, finding parent tags as we go up.
    tag_nodes = left_leaves
    tags = OrderedSet((n.tag for n in tag_nodes))
    while len(tags) > 0:
        for tag in tags:
            # Get a chain of nodes from each side with the given tag
            left_chain = OrderedSet((n for n in left_nodes if n.tag == tag))
            right_chain = OrderedSet((n for n in right_nodes if n.tag == tag))

            longest_common = lcs(left_chain, right_chain, equal_match)
            matches.update((Match(l, r) for l, r in longest_common))

        tag_nodes = [n.getparent() for n in tag_nodes if
                     n.getparent() is not None]
        tags = OrderedSet((n.tag for n in tag_nodes))

    return matches


# Find a partner for a given node in the matches set
def matching_partner(matches, node):
    """ Given a set of Match objects, find a Match that contains the
        given node, and return its partner. """
    try:
        match, = (m for m in matches if node in m)
    except ValueError:
        return None

    partner = match.b if match.a == node else match.a
    return partner


def editscript(left_root, right_root, matches):
    """
    Return an "edit script", a set of actions that transform the left
    tree into the right tree, for the given pair of trees with the given
    minimum-cost match set.
    """

    script = OrderedSet()

    # If the trees don't have the same signature (see function doc for
    # what that means) We can't transform the left into the right.
    if getpath(left_root) != getpath(right_root):
        return script

    # Add the roots of both if they don't already exist in matches
    if Match(left_root, right_root) not in matches:
        matches.add(Match(left_root, right_root))

    for right_child in right_root.xpath(".//*"):
        # There's no reason for this not to exist since we're descending
        # down the tree.
        right_parent = right_child.getparent()

        # See if our right child already has a partner
        left_child = matching_partner(matches, right_child)

        # If it does not have a partner, add an INSERT for it
        if left_child is None:
            # Find the parent's partner, if there is one
            # Note: this should exist already because we're visiting nodes
            # from the root down. If it doesn't, something has gone wrong
            # somewhere.
            # XXX: We should probably check to make sure it exists.
            left_parent = matching_partner(matches, right_parent)

            # Get the node's index in its parent
            index = right_parent.index(right_child)

            # Add the insert for the node to the edit script
            action = INSERT(etree.tostring(right_child),
                            getpath(right_parent),
                            index)
            script.add(action)

            # Perform the action on our working copy of the left
            # tree so we'll be able to introspect
            transform(left_root, set([action, ]))

            # Get the left child so we can use it in alignment later
            # left_child = etree.fromstring(action.node)
            left_child = left_root.xpath(getpath(right_child))[0]

            # Add the match to our master set of matching nodes
            matches.add(Match(left_child, right_child))

        # The right node has a partner already and is not a root node
        elif right_parent is not None:
            # This should exist either having been added by a previous
            # cycle or having already existed
            left_parent = left_child.getparent()

            # See if the "value" (the text) of the elements differ
            if right_child.text != left_child.text or \
                    right_child.tail != left_child.tail or \
                    right_child.attrib != left_child.attrib:

                # If so, add an update for the node
                action = UPDATE(getpath(right_child),
                                right_child.text,
                                right_child.tail,
                                frozenset(right_child.attrib.items()))
                script.add(action)

                # Perform the action on our working copy of the left
                # tree so we'll be able to introspect
                transform(left_root, set([action, ]))

            # See if we've got a mis-match between parents or a change
            # in parental index
            if (Match(left_parent, right_parent) not in matches) or \
                    left_parent.index(left_child) != \
                    right_parent.index(right_child):
                # Get the left parent's right partner
                right_parent = matching_partner(matches, left_parent)
                if right_parent is None:
                    # The left_parent doesn't have a match (it might be
                    # deleted). Use what the right_child reports as its
                    # parent.
                    # XXX: Can we assume that this will be a valid
                    # parent here?
                    right_parent = right_child.getparent()

                # Get the right index
                index = right_parent.index(right_child)

                # If so, add a move action for the node to the script
                action = MOVE(getpath(left_child),
                              getpath(right_parent),
                              index)
                script.add(action)

                # Perform the action on our working copy of the left
                # tree so we'll be able to introspect
                transform(left_root, set([action, ]))

        # Align the child nodes
        left_children = left_child.getchildren()
        right_children = right_child.getchildren()

        # Find all left_child children whose parners are children of
        # right_child. We'll handle any that aren't in the deletion
        # phase.
        left_match_children = [n for n in left_children
                               if matching_partner(matches, n)
                               in right_children]
        common_sequence = lcs(left_child, right_child,
                              lambda l, r: Match(l, r) in matches)

        for left_child, right_child in \
                zip(left_match_children, right_children):
            if (left_child, right_child) in common_sequence:
                # these are already aligned
                continue

            # Get the right index
            index = right_child.getparent().index(right_child)

            # Add a move action for the node to the script
            action = MOVE(getpath(left_child), getpath(right_parent), index)
            script.add(action)

            # Perform the action on our working copy of the left
            # tree so we'll be able to introspect
            transform(left_root, set([action, ]))

    # If there any nodes we've haven't visited in left_tree that we did
    # in right_tree (that don't now have a match in matches), they need
    # to be deleted.
    for left_child in reversed(left_root.xpath("//*")):
        right_child = matching_partner(matches, left_child)
        if right_child is None:
            # Add a delete action for this node to the script
            action = DELETE(getpath(left_child))
            script.add(action)

            # Perform the action on our working copy of the left
            # tree so we'll be able to introspect
            transform(left_root, set([action, ]))

    return script


def transform(tree, script):
    """ Transform the tree using the given edit script """

    for action in script:
        # Perform an insert action. This inserts a node into a given
        # parent at a given index.
        if type(action) == INSERT:
            node = etree.fromstring(action.node)
            parent = tree.xpath(action.parent)[0]
            parent.insert(action.index, node)

        # Perform an update action. This updates the text, tail, and
        # attributes of the given node.
        if type(action) == UPDATE:
            node = tree.xpath(action.path)[0]
            node.text = action.text
            node.tail = action.tail
            (node.set(k, v) for k, v in action.attrib)

        # Perform a move action. This moves the given node from its
        # existing parent to a given index within a new parent.
        if type(action) == MOVE:
            node = tree.xpath(action.path)[0]
            parent = tree.xpath(action.parent)[0]

            # lxml's insert will "move" by default
            # XXX: What happens to element "tail" text when we move? Is
            # that something we should be concerned with?
            parent.insert(action.index, node)

        # Perform a delete action. This removes the given node from its
        # parent.
        if type(action) == DELETE:
            node = tree.xpath(action.path)[0]
            node.getparent().remove(node)

    return tree


def diff(left_tree, right_tree, match=simplematch,
         match_threshold=THRESHOLD):
    """ Return difference between the left tree and the right tree as an
        edit script that will transform the left into the right.

        Optionally, an element matching function can be provided
        (simplematch and fastmatch are included, simplematch is the
        default) and a matching threshold. """

    # We're going to need to operate on the left tree, but we want to do
    # it non-destructively, so we'll make a copy of it.
    left_tree = deepcopy(left_tree)

    # Get the match set
    matches = match(left_tree, right_tree, threshold=match_threshold)

    # Get the edit script
    edit_script = editscript(left_tree, right_tree, matches)

    return edit_script

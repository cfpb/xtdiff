# xtdiff: XML Tree Diff

[![Build Status](https://travis-ci.org/cfpb/xtdiff.svg?branch=master)](https://travis-ci.org/cfpb/xtdiff)

XML Tree Diff is a Python library that implements ["Change detection in 
hierarchically structured information", by Sudarshan S. Chawathe, Anand 
Rajaraman, Hector Garcia-Molina, and Jennifer Widom.](http://ilpubs.stanford.edu:8090/115/1/1995-46.pdf).

This means it is a library that will compare two (lxml) XML trees and
generates a set of actions that will transform one of the trees into the
other. The actions are in the form of an ordered set of either `INSERT`,
`UPDATE`, `MOVE`, or `DELETE`, when performed in order they will
transform the first tree into the second.

- [Requirements](#requirements)
- [Installation](#installation)
- [Using xtdiff](#using-xtdiff)
    - [Generating Diffs](#generating-diffs)
    - [Applying Diffs](#applying-diffs)
- [Licensing](#licensing)


## Requirements

It supports Python 2.7 and Python 3.4, but really, you should be using
Python 3, shouldn't you?

xtdiff requires:

- [lxml](http://lxml.de/)


## Installation

xtdiff can be installed as a Python package:

```shell
pip install git+https://github.com/cfpb/xtdiff
```

## Using xtdiff


```python
>>> from lxml import etree
>>> import xtdiff
```

### Generating Diffs

xtdiff has a `diff()` function that takes two lxml elements and returns
an ordered set of actions that will transform the first (hereafter
referred to as the "left") into the second (hereafter referred to as the
"right").

There are four possible actions that can be performed, `INSERT`,
`UPDATE`, `MOVE`, and `DELETE`.

#### Insertions

When the right tree contains nodes that are not found in the left tree,
the `INSERT` action will be returned as part of the set of actions.

The `INSERT` action includes the node to be inserted as a string, the
XPath to the parent in which to insert the node, and the index at which
it should be inserted into the parent.

```python
>>> left = """<root>
... </root>"""
>>> right = """<root>
...   <para>Lorem ipsum dolor sit amet</para>
... </root>"""
>>> xtdiff.diff(etree.fromstring(left), etree.fromstring(right))
OrderedSet([
    INSERT(node=b'<para>Lorem ipsum dolor sit amet</para>\n', 
           parent='/root', 
           index=0)
])
```

#### Updates

When both the left and right tree contain the same node, but the
text contents or attributes of that node have changed, an `UPDATE` 
action will be returned as part of the set of actions.

The `UPDATE` action includes the XPath to the node that needs to be
updated along with the new text, tail, and attributes.

```python
>>> left = """<root>
...   <para>Lorem ipsum dolor sit amet</para>
... </root>"""
>>> right = """<root>
...   <para>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</para>
... </root>"""
>>> xtdiff.diff(etree.fromstring(left), etree.fromstring(right))
OrderedSet([
    UPDATE(path='/root/para', 
           text='Lorem ipsum dolor sit amet, consectetur adipiscing elit.', 
           tail='\n', 
           attrib=frozenset())
])
```

#### Moves

When both the left and right tree contain the same node, but the node
has a different parent, or is located at a different place within the
same parent, a `MOVE` action will be returned as part of the set of 
actions.

The `MOVE` action includes the XPath to the node that needs to be
moved the XPath to the node's (possibly new) parent, and the index at 
which it should be inserted into the parent.

```python
>>> left = """<root>
...   <para>Cras tellus turpis, tincidunt tristique ipsum aliquam, semper mollis nisi.</para>
...   <para>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</para>
... </root>"""
>>> right = """<root>
...   <para>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</para>
...   <para>Cras tellus turpis, tincidunt tristique ipsum aliquam, semper mollis nisi.</para>
</root>"""
>>> xtdiff.diff(etree.fromstring(left), etree.fromstring(right))
OrderedSet([
    MOVE(path='/root/para[2]', parent='/root', index=0)
])
```

#### Deletions

When the left tree contains a node that does not appear in the right
tree, a `DELETE` action will be returned as part of the set of 
actions.

The `DELETE` action includes the XPath to the node that needs to be
deleted.

```python
>>> left = """<root>
...   <para>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</para>
...   <para>Cras tellus turpis, tincidunt tristique ipsum aliquam, semper mollis nisi.</para>
... </root>"""
>>> right = """<root>
...   <para>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</para>
</root>"""
>>> xtdiff.diff(etree.fromstring(left), etree.fromstring(right))
OrderedSet([
    DELETE(path='/root/para[2]')
])
```

### Applying Diffs

xtdiff includes a function, `transform()`, that will apply a set of
actions returned by the `diff` function to the lxml element given.

```python
>>> left = """<root>
... </root>"""
>>> left_root = etree.fromstring(left)
>>> right = """<root>
...   <para>Lorem ipsum dolor sit amet</para>
... </root>"""
>>> right_root = etree.fromstring(right)
>>> actions = xtdiff.diff(left_root, right_root)
>>> new_root = xtdiff.transform(left_tree, actions)
>>> etree.tostring(new_root)
<root>
  <para>Lorem ipsum dolor sit amet</para>
</root>"
```

## Licensing 
1. [TERMS](TERMS.md)
2. [LICENSE](LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)


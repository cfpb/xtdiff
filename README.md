# :warning: THIS REPO IS DEPRECATED (6/1/2018) :warning:

# xtdiff: XML Tree Diff

[![Build Status](https://travis-ci.org/cfpb/xtdiff.svg?branch=master)](https://travis-ci.org/cfpb/xtdiff)

XML Tree Diff is a Python library that implements ["Change detection in 
hierarchically structured information", by Sudarshan S. Chawathe, Anand 
Rajaraman, Hector Garcia-Molina, and Jennifer Widom.](http://ilpubs.stanford.edu:8090/115/1/1995-46.pdf).

This means it is a library that will compare two (lxml) XML trees and
generate a set of actions that will transform one tree into the
other.

- [Requirements](#requirements)
- [Installation](#installation)
- [Using xtdiff](#using-xtdiff)
    - [`diff()`: Generating diffs](#diff-generating-diffs)
    - [`transform()`: Applying diffs](#transform-applying-diffs)
    - [`xsldiff()`: Generating XSL diffs](#xsldiff-generating-xsl-diffs)
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

### `diff()`: Generating diffs

xtdiff has a `diff()` function that takes two lxml `Element` objects 
and returns an ordered set of actions as an `OrderedSet` that will 
transform the first (hereafter referred to as the "left") into the 
second (hereafter referred to as the "right").

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

### `transform()`: Applying diffs

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

### `xsldiff()`: Generating XSL diffs

xtdiff can also generate an XSL stylesheet that can be used to transform
the left XML document into the right document. The API for generating
XSL diffs is the same as for generating an `OrderedSet` edit script
outlined above.

The `xsldiff()` function takes a left lxml `Element` and a right lxml
`Element` and returns an `Element` representing the XSL stylesheet. The
stylesheet can then be writen to disk an applied to the original
document as needed.

```python
>>> left = "..."
>>> right = "..."
>>> xsl = xtdiff.xsldiff(etree.fromstring(left), etree.fromstring(right))
>>> etree.tostring(xsl)
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  ...
</xsl:stylesheet>
```

An existing `OrderedSet` edit script can also be serialized to XSL with
the `toxsl()` function:

```python
>>> actions = xtdiff.diff(left_root, right_root)
>>> xsl = xtdiff.toxsl(actions)
>>> etree.tostring(xsl)
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  ...
</xsl:stylesheet>
```

**NOTE**: The XSL stylesheet will only work with the specific left 
document it was generated for, not documents comforming to its schema 
generally.


## Licensing 
1. [TERMS](TERMS.md)
2. [LICENSE](LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)


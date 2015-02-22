# Copyright (c) 2015, Freja Nordsiek
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Tests for SettingsTree.Tree. """

import copy
import math
import posixpath
import random
import string
import collections

from nose.tools import raises

from SettingsTree import Tree, Leaf


random.seed()

# Need a string containing all the characters we will use for paths.
ltrs = string.ascii_letters + string.digits

# Make a group of random leaves
random_leaves = collections.OrderedDict()
for i in range(20, 40):
    name = ''.join([random.choice(ltrs)
                   for j in range(0, random.randint(4, 9))])
    random_leaves[name] = Leaf(value=random.random())

# Make a group of random leaves and empty trees
random_treesAndLeaves = collections.OrderedDict()
for i in range(20, 40):
    name = ''.join([random.choice(ltrs)
                   for j in range(0, random.randint(4, 9))])
    if random.randrange(2) == 0:
        random_treesAndLeaves[name] = Leaf(value=random.random())
    else:
        random_treesAndLeaves[name] = Tree()

# Make a group of random leaves with full paths to them.
random_path_leaves = dict()
for i in range(20, 40):
    depth = random.randint(1, 6)
    path = '/'
    for j in range(0, depth):
        path = posixpath.join(path, \
            ''.join([random.choice(ltrs) \
            for j in range(0, random.randint(4, 9))]))
    random_path_leaves[path] = Leaf(value=random.random())

# A of random set of parameters to use.
rand_params = dict()
for i in range(random.randint(5, 10)):
    k = ''.join([random.choice(ltrs) for j in range(0, 20)])
    v = random.random()
    rand_params[k] = v

# Test initializing a blank one.
def test_initialize_tree_blank():
    tree = Tree()

# Test initializing a Tree with a bunch of random Leaves.
def test_initialize_tree_leaves():
    tree = Tree(children=random_leaves)

# Test initializing a Tree with some empty Trees.
def test_initialize_tree_trees():
    tree = Tree(children=dict([(k, Tree()) for k in random_leaves]))

# Test initializing a Tree with some Leaves and empty Trees.
def test_initialize_tree_leavesAndTrees():
    tree = Tree(children=random_treesAndLeaves)

# Test initializing a Tree with nested paths to random Leaves.
def test_initialize_tree_paths():
    tree = Tree(children=random_path_leaves)

# Test initializing with a non-Mappable.
@raises(TypeError)
def test_initialize_tree_invalid_nonMappable():
    tree = Tree(children=random.random())

# Test initializing with something that isn't a Leaf or Tree.
@raises(TypeError)
def test_initialize_tree_invalid_nonLeafTree():
    children = copy.deepcopy(random_leaves)
    children[random.choice(tuple(children.keys()))] = random.random()
    tree = Tree(children=children)


# Test __len__
def test_len():
    for i in range(len(random_leaves)):
        children = collections.OrderedDict( \
            tuple(random_leaves.items())[:i])
        tree = Tree(children=children)
        assert len(children) == len(tree)

# Test __contains__
def test_in():
    tree = Tree(children=random_leaves)
    for k in random_leaves:
        assert k in tree

def test_not_in():
    tree = Tree(children=random_leaves)
    for i in range(100):
        name = None
        while name is None or name in random_leaves:
            name = ''.join([random.choice(ltrs)
                           for j in range(0, random.randint(4, 9))])
        assert name not in tree

# Test __iter__
def test_iteration():
    tree = Tree(children=random_leaves)
    keys = [k for k in tree]
    assert list(random_leaves.keys()) == keys

# Test keys.
def test_keys():
    tree = Tree(children=random_leaves)
    assert tuple(random_leaves.keys()) == tuple(tree.keys())

# Test items.
def test_items():
    tree = Tree(children=random_leaves)
    assert tuple(random_leaves.items()) == tuple(tree.items())


# Test get access.

def test_get_root():
    tree = Tree(children=random_treesAndLeaves)
    assert tree == tree[2 * posixpath.sep]

def test_get_root_children():
    tree = Tree(children=random_treesAndLeaves)
    assert list(random_treesAndLeaves.keys()) \
        == tree[posixpath.sep]

def test_get_leaf():
    tree = Tree(children=random_leaves)
    for k, v in random_leaves.items():
        assert v == tree[k + posixpath.sep]

def test_get_leaf_value():
    tree = Tree(children=random_leaves)
    for k, v in random_leaves.items():
        assert v.value == tree[k]

def test_get_nested_leaf():
    tree = Tree(children=random_path_leaves)
    for k, v in random_path_leaves.items():
        assert v == tree[k + posixpath.sep]

def test_get_nested_leaf_value():
    tree = Tree(children=random_path_leaves)
    for k, v in random_path_leaves.items():
        assert v.value == tree[k]

def test_get_leaf_extraParameter():
    name = 'aivnennb'
    tree = Tree(children={name: Leaf(**rand_params)})
    for k, v in rand_params.items():
        assert v == tree[posixpath.join(name, k)]

def test_get_tree():
    name = 'avaivneav'
    tree1 = Tree(children=random_leaves)
    tree2 = Tree(children={name: tree1})
    assert tree1 == tree2[name + posixpath.sep]

def test_get_tree_children():
    name = 'avaivneav'
    tree1 = Tree(children=random_leaves)
    tree2 = Tree(children={name: tree1})
    assert list(tree1.keys()) == tree2[name]

def test_get_invalid_missing():
    tree = Tree(children=random_leaves)
    for i in range(100):
        name = None
        while name is None or name in random_leaves:
            name = ''.join([random.choice(ltrs)
                           for j in range(0, random.randint(4, 9))])
        try:
            v = tree[name + posixpath.sep]
        except KeyError:
            threw_error = True
        else:
            threw_error = False
        assert threw_error

def test_get_invalid_missing_grabValue():
    tree = Tree(children=random_leaves)
    for i in range(100):
        name = None
        while name is None or name in random_leaves:
            name = ''.join([random.choice(ltrs)
                           for j in range(0, random.randint(4, 9))])
        try:
            v = tree[name]
        except KeyError:
            threw_error = True
        else:
            threw_error = False
        assert threw_error

def test_get_invalid_missing_subtree():
    tree = Tree(children=random_leaves)
    for i in range(100):
        name = None
        while name is None or name in random_leaves:
            name = ''.join([random.choice(ltrs)
                           for j in range(0, random.randint(4, 9))])
        try:
            v = tree[name + posixpath.sep + 'aviave']
        except KeyError:
            threw_error = True
        else:
            threw_error = False
        assert threw_error

def test_get_invalid_leaf_extraParameter_missing():
    name = 'aivnennb'
    tree = Tree(children={name: Leaf(**rand_params)})
    for i in range(100):
        name2 = None
        while name2 is None or name2 in rand_params:
            name2 = ''.join([random.choice(ltrs)
                           for j in range(0, random.randint(4, 9))])
        try:
            v = tree[posixpath.join(name, name2)]
        except KeyError:
            threw_error = True
        else:
            threw_error = False
        assert threw_error

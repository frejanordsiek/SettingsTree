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
    depth = random.randint(4, 6)
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

@raises(KeyError)
def test_get_invalid_nonTreeLeafInChildren():
    tree = Tree(children=random_leaves)
    name = None
    while name is None or name in random_leaves:
        name = ''.join([random.choice(ltrs)
                       for j in range(0, random.randint(4, 9))])
    tree._children[name] = random.random()
    v = tree[name]

@raises(KeyError)
def test_get_invalid_nested_nonTreeLeafInChildren():
    tree = Tree(children=random_leaves)
    name = None
    while name is None or name in random_leaves:
        name = ''.join([random.choice(ltrs)
                       for j in range(0, random.randint(4, 9))])
    name2 = ''.join([random.choice(ltrs)
                    for j in range(0, random.randint(4, 9))])
    tree._children[name] = random.random()
    v = tree[posixpath.join(name, name2)]


# Test set access.

def test_set_leaf():
    tree = Tree()
    for k, v in random_leaves.items():
        tree[k] = v
        assert tree[k + posixpath.sep] == v
    assert len(tree) == len(random_leaves)

def test_set_leaf_value():
    values = [(k, random.random()) for k in random_leaves]
    tree = Tree(children=random_leaves)
    for k, v in values:
        tree[k] = v
        assert v == tree[k]
    assert len(tree) == len(random_leaves)

def test_set_tree():
    name = 'nvienva'
    tree1 = Tree()
    tree2 = Tree()
    tree2[name] = tree1
    assert tree1 == tree2[name + posixpath.sep]

def test_set_tree_overwrite():
    name = random.choice(tuple(random_leaves.keys()))
    tree1 = Tree()
    tree2 = Tree(children=random_leaves)
    tree2[name] = tree1
    assert tree1 == tree2[name + posixpath.sep]
    assert len(random_leaves) == len(tree2)

def test_set_leaf_overwrite():
    name = random.choice(tuple(random_leaves.keys()))
    tree = Tree()
    leaf = Leaf()
    for k in random_leaves:
        tree[k] = Tree()
    tree[name] = leaf
    assert leaf == tree[name + posixpath.sep]
    assert len(random_leaves) == len(tree)

def test_set_nested_leaf():
    name = 'nvienva'
    tree = Tree(children={name: Tree()})
    for k, v in random_leaves.items():
        tree[posixpath.join(name, k)] = v
        assert v == tree[posixpath.join(name, k) + posixpath.sep]
    assert len(tree[name]) == len(random_leaves)

def test_set_nested_leaf_value():
    name = 'nvienva'
    values = [(k, random.random()) for k in random_leaves]
    tree = Tree(children={name: Tree(children=random_leaves)})
    for k, v in values:
        tree[posixpath.join(name, k)] = v
        assert v == tree[posixpath.join(name, k)]
    assert len(tree[name]) == len(random_leaves)

def test_set_leaf_extraParameter():
    name = 'aivnennb'
    tree = Tree(children={name: Leaf()})
    for k, v in rand_params.items():
        tree[posixpath.join(name, k)] = v
        assert v == tree[posixpath.join(name, k)]
    assert len(rand_params) == len(tree[name + posixpath.sep])

@raises(KeyError)
def test_set_invalid_root():
    tree = Tree(children=random_leaves)
    tree[posixpath.sep] = Tree()

@raises(KeyError)
def test_set_invalid_value_missing():
    tree = Tree(children=random_leaves)
    name = None
    while name is None or name in random_leaves:
        name = ''.join([random.choice(ltrs)
                       for j in range(0, random.randint(4, 9))])
    tree[name] = random.random()

@raises(TypeError)
def test_set_invalid_tree_value():
    tree = Tree(children=random_leaves)
    name = None
    while name is None or name in random_leaves:
        name = ''.join([random.choice(ltrs)
                       for j in range(0, random.randint(4, 9))])
    tree[name] = Tree()
    tree[name] = random.random()

@raises(KeyError)
def test_set_invalid_nonTreeLeafInChildren():
    tree = Tree(children=random_leaves)
    name = None
    while name is None or name in random_leaves:
        name = ''.join([random.choice(ltrs)
                       for j in range(0, random.randint(4, 9))])
    tree._children[name] = random.random()
    tree[name] = random.random()

@raises(KeyError)
def test_set_invalid_nested_nonTreeLeafInChildren():
    tree = Tree(children=random_leaves)
    name = None
    while name is None or name in random_leaves:
        name = ''.join([random.choice(ltrs)
                       for j in range(0, random.randint(4, 9))])
    name2 = ''.join([random.choice(ltrs)
                    for j in range(0, random.randint(4, 9))])
    tree._children[name] = random.random()
    tree[posixpath.join(name, name2)] = random.random()


# Test del access

def test_del_leaf():
    tree = Tree(children=random_leaves)
    keys = tuple(random_leaves.keys())
    for i in reversed(range(len(keys))):
        del tree[keys[i]]
        assert keys[i] not in tree
        assert i == len(tree)

def test_del_tree():
    tree = Tree(children={k: Tree() for k in random_leaves})
    keys = tuple(random_leaves.keys())
    for i in reversed(range(len(keys))):
        del tree[keys[i]]
        assert keys[i] not in tree
        assert i == len(tree)

def test_del_nested_leaf():
    name = 'nvienva'
    tree = Tree(children={name: Tree(children=random_leaves)})
    keys = tuple(random_leaves.keys())
    for i in reversed(range(len(keys))):
        del tree[posixpath.join(name, keys[i])]
        assert posixpath.join(name, keys[i]) not in tree
        assert i == len(tree[name + posixpath.sep])

def test_del_nested_tree():
    name = 'nvienva'
    tree = Tree(children={name: Tree(
                children=dict([(k, Tree()) for k in random_leaves]))})
    keys = tuple(random_leaves.keys())
    for i in reversed(range(len(keys))):
        del tree[posixpath.join(name, keys[i])]
        assert posixpath.join(name, keys[i]) not in tree
        assert i == len(tree[name + posixpath.sep])

def test_del_leaf_extraParameter():
    name = 'aivnennb'
    tree = Tree(children={name: Leaf(**rand_params)})
    keys = tuple(rand_params.keys())
    for i in reversed(range(len(keys))):
        del tree[posixpath.join(name, keys[i])]
        assert posixpath.join(name, keys[i]) not in tree
        assert i == len(tree[name + posixpath.sep])

@raises(KeyError)
def test_del_invalid_root():
    tree = Tree(children=random_leaves)
    del tree[posixpath.sep]

@raises(KeyError)
def test_del_invalid_missing():
    tree = Tree(children=random_leaves)
    name = None
    while name is None or name in random_leaves:
        name = ''.join([random.choice(ltrs)
                       for j in range(0, random.randint(4, 9))])
    del tree[name]

@raises(KeyError)
def test_del_invalid_nested_nonTreeLeafInChildren():
    tree = Tree(children=random_leaves)
    name = None
    while name is None or name in random_leaves:
        name = ''.join([random.choice(ltrs)
                       for j in range(0, random.randint(4, 9))])
    name2 = ''.join([random.choice(ltrs)
                    for j in range(0, random.randint(4, 9))])
    tree._children[name] = random.random()
    del tree[posixpath.join(name, name2)]


# Call _getsetdel_item with an invalid operation
@raises(ValueError)
def test_getsetdel_item_invalid_operation():
    tree = Tree(children=random_leaves)
    name = random.choice(tuple(random_leaves.keys()))
    tree._getsetdel_item(path=name, operation='avaj')


# Test list_all.

def test_list_all_empty_tree():
    tree = Tree()
    for tp in ('all', 'tree', 'leaf'):
        assert 0 == len(tree.list_all(tp=tp))

def test_list_all_just_leaves():
    tree = Tree(children=random_leaves)
    assert 0 == len(tree.list_all(tp='tree'))
    names = tree.list_all(tp='leaf')
    assert names == tree.list_all(tp='all')
    assert len(names) == len(random_leaves)
    assert len(names) == len(set(names))
    for name in names:
        assert 1 == name.count(posixpath.sep)
        assert name[0] == posixpath.sep
        assert name in tree
        assert name[1:] in random_leaves

def test_list_all_just_trees():
    tree = Tree(children=dict([(k, Tree()) for k in random_leaves]))
    assert 0 == len(tree.list_all(tp='leaf'))
    names = tree.list_all(tp='tree')
    assert names == tree.list_all(tp='all')
    assert len(names) == len(random_leaves)
    assert len(names) == len(set(names))
    for name in names:
        assert 1 == name.count(posixpath.sep)
        assert name[0] == posixpath.sep
        assert name in tree
        assert name[1:] in random_leaves

def test_list_all_mixed():
    tps = ('all', 'tree', 'leaf')
    tree = Tree(children=random_path_leaves)
    names = dict([(tp, tuple(tree.list_all(tp=tp))) for tp in tps])
    for tp in tps:
        assert len(names[tp]) == len(set(names[tp]))
    assert len(names['all']) == len(names['tree']) + len(names['leaf'])
    assert 0 == len(set(names['tree']).intersection(set(names['leaf'])))
    assert sorted(names['all']) == sorted(names['leaf'] + names['tree'])
    assert len(random_path_leaves) == len(names['leaf'])
    assert sorted(list(random_path_leaves.keys())) \
        == sorted(names['leaf'])
    for name in names['all']:
        assert name in tree
        assert posixpath.sep == name[0]
    for name in names['tree']:
        assert isinstance(tree[name + posixpath.sep], Tree)
        count = 0
        for s in random_path_leaves:
            if s.startswith(name):
                count += 1
        assert 1 == count

@raises(ValueError)
def test_list_all_invalid_type():
    tree = Tree(children=random_path_leaves)
    v = tree.list_all(tp='anvienviavjonba')


# Test diff

def test_diff_identical():
    tree1 = Tree(children=random_path_leaves)
    tree2 = Tree(children=random_path_leaves)
    assert ([], [], []) == tree1.diff(tree2)

def test_diff_different_subsets():
    length = len(random_path_leaves)
    for i in range(10):
        number = random.randrange(int(math.floor(0.33 * length)),
                                  int(math.floor(0.66 * length)))
        leaves1 = dict(random.sample(random_path_leaves.items(),
                       number))
        leaves2 = dict(random.sample(random_path_leaves.items(),
                       number))
        tree1 = Tree(children=leaves1)
        tree2 = Tree(children=leaves2)
        different_values, only_in_1, only_in_2 = tree1.diff(tree2)
        assert 0 == len( \
            set(different_values).intersection(set(only_in_1)))
        assert 0 == len( \
            set(different_values).intersection(set(only_in_2)))
        assert 0 == len(set(only_in_1).intersection(set(only_in_2)))
        for name in different_values:
            assert name in leaves1
            assert name in leaves2
        for name in only_in_1:
            assert name in leaves1
            assert name not in leaves2
        for name in only_in_2:
            assert name not in leaves1
            assert name in leaves2

def test_diff_different_values():
    length = len(random_path_leaves)
    for i in range(10):
        leaves1 = copy.deepcopy(random_path_leaves)
        leaves2 = copy.deepcopy(leaves1)
        number = random.randrange(int(math.floor(0.33 * length)),
                                  int(math.floor(0.66 * length)))
        keys = random.sample(list(leaves1.keys()), number)
        for k in keys:
            while leaves1[k].value == leaves2[k].value:
                leaves2[k].value = random.random()
        tree1 = Tree(children=leaves1)
        tree2 = Tree(children=leaves2)
        different_values, only_in_1, only_in_2 = tree1.diff(tree2)
        assert 0 == len(only_in_1)
        assert 0 == len(only_in_2)
        assert sorted(keys) == sorted(different_values)

@raises(TypeError)
def test_diff_invalid_nonTree():
    tree = Tree(children=random_path_leaves)
    tree.diff(tree=random.random())


# test get_values

def test_get_values_paths():
    tree = Tree(children=random_path_leaves)
    values = dict([(k, v.value) for k, v in random_path_leaves.items()])
    assert values == tree.get_values(form='paths')

def test_get_values_nested():
    values = dict()
    tree = Tree()
    for i in range(1000):
        path = [random.choice(ltrs) for i in range(10)]
        val_ptr = values
        for k in range(len(path) - 1):
            if path[k] not in val_ptr:
                val_ptr[path[k]] = dict()
            val_ptr = val_ptr[path[k]]
        val_ptr[path[-1]] = random.random()
        tree[posixpath.join(*path)] = Leaf(value=val_ptr[path[-1]])
    assert values == tree.get_values(form='nested')

@raises(ValueError)
def test_get_values_invalid_form():
    tree = Tree(children=random_path_leaves)
    tree.get_values(form='anvien2')


# Test set_values

def test_set_values_paths():
    tree = Tree(children=random_path_leaves)
    values = dict([(k, random.random()) for k in random_path_leaves])
    tree.set_values(values=values)
    assert values == tree.get_values(form='paths')

def test_set_values_nested():
    values = dict()
    tree = Tree()
    for i in range(1000):
        path = [random.choice(ltrs) for i in range(10)]
        val_ptr = values
        for k in range(len(path) - 1):
            if path[k] not in val_ptr:
                val_ptr[path[k]] = dict()
            val_ptr = val_ptr[path[k]]
        val_ptr[path[-1]] = random.random()
        tree[posixpath.join(*path)] = Leaf(value=random.random())
    tree.set_values(values=values)
    assert values == tree.get_values(form='nested')

def test_set_values_paths_missing():
    tree = Tree(children=random_path_leaves)
    values = dict([(k, random.random()) for k in random_path_leaves])
    name = None
    while name is None or name in values:
        name = ''.join([random.choice(ltrs)
                       for j in range(0, random.randint(4, 9))])
    values2 = copy.deepcopy(values)
    values2[name] = random.random()
    tree.set_values(values=values2)
    assert values == tree.get_values(form='paths')

def test_set_values_paths_nonMappingInput():
    tree = Tree(children=random_path_leaves)
    values = dict([(k, v.value) for k, v in random_path_leaves.items()])
    name = random.choice(tuple(values.keys()))
    name2 = posixpath.sep \
        + posixpath.join(*name.split(posixpath.sep)[:3])
    values2 = copy.deepcopy(values)
    del values2[name]
    values2[name2] = random.random()
    tree.set_values(values=values2)
    values_out = tree.get_values(form='paths')
    assert values2 != values_out
    assert values == values_out

@raises(TypeError)
def test_set_values_invalid_form():
    tree = Tree(children=random_path_leaves)
    tree.set_values(values='anvien2')


# Test find_invalids and is_valid together

def test_validity_allValid():
    tree = Tree(children=random_path_leaves)
    assert 0 == len(tree.find_invalids())
    assert tree.is_valid()

def test_validity_differentNumbersOfInvalids():
    names = tuple(random_path_leaves.keys())
    for i in range(len(random_path_leaves)):
        keys = random.sample(names, i)
        leaves = copy.deepcopy(random_path_leaves)
        for k in keys:
            leaves[k].validator_function = lambda x, y: False
        tree = Tree(children=leaves)
        invalids = tree.find_invalids()
        assert i == len(invalids)
        assert sorted(keys) == sorted(invalids)
        assert (i != 0) != tree.is_valid()

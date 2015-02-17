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

""" Tests for SettingsTree.Leaf. """

import copy
import math
import random
import string
import collections
import unittest

from nose.tools import raises

from SettingsTree import Leaf


random.seed()


# A of random set of parameters to use.
rand_params = dict()


def setup_module():
    rand_params = dict()
    ltrs = string.ascii_letters + string.digits
    for i in range(random.randint(5, 10)):
        k = ''.join([random.choice(ltrs) for j in range(0, 20)])
        v = random.random()
        rand_params[k] = v


# Test initializing a blank one.
def test_blank_leaf():
    leaf = Leaf()


# Test initializing one with everything set
def test_fully_initialized_leaf():
    leaf = Leaf(value=3, valid_value_types=[int, float],
                allowed_values=(3, 4), forbidden_values=(3,),
                validators=[('GreaterThan', 2)],
                validator_function=lambda x,y: True,
                blah=10)


# Test setting the value.
def test_set_value():
    leaf = Leaf()
    x = random.random()
    leaf.value = x
    assert x == leaf.value


# Test all correct ways to set valid_value_types and a few incorrect
# ones.

def test_undo_valid_value_types():
    leaf = Leaf()
    x = None
    leaf.valid_value_types = x
    assert x == leaf.valid_value_types


def test_set_valid_value_types_one_type():
    leaf = Leaf()
    x = int
    leaf.valid_value_types = x
    out = leaf.valid_value_types
    assert isinstance(out, collections.Iterable)
    assert len(out) == 1
    assert x == out[0]


def test_set_valid_value_types_many_types():
    leaf = Leaf()
    x = (int, float, type(None))
    leaf.valid_value_types = x
    out = leaf.valid_value_types
    assert isinstance(out, collections.Iterable)
    assert len(x) == len(out)
    for i, v in enumerate(x):
        assert v == out[i]


@raises(TypeError)
def test_set_valid_value_types_one_invalid():
    leaf = Leaf()
    x = 3
    leaf.valid_value_types = x


@raises(TypeError)
def test_set_valid_value_types_list_with_one_invalid():
    leaf = Leaf()
    x = [int, 'av', float, bytes]
    leaf.valid_value_types = x


# Test all correct ways to set allowed_values and a few incorrect
# ones.

def test_undo_allowed_values():
    leaf = Leaf()
    x = None
    leaf.allowed_values = x
    assert x == leaf.allowed_values


def test_set_allowed_values():
    leaf = Leaf()
    x = [random.random() for i in range(random.randint(4, 30))]
    leaf.allowed_values = x
    out = leaf.allowed_values
    assert isinstance(out, collections.Iterable)
    assert len(x) == len(out)
    for i, v in enumerate(x):
        assert v == out[i]


@raises(TypeError)
def test_set_allowed_values_invalid_noniterable():
    leaf = Leaf()
    x = 9
    leaf.allowed_values = x


# Test all correct ways to set forbidden_values and a few incorrect
# ones.

def test_undo_forbidden_values():
    leaf = Leaf()
    x = None
    leaf.forbidden_values = x
    assert x == leaf.forbidden_values


def test_set_forbidden_values():
    leaf = Leaf()
    x = [random.random() for i in range(random.randint(4, 30))]
    leaf.forbidden_values = x
    out = leaf.forbidden_values
    assert isinstance(out, collections.Iterable)
    assert len(x) == len(out)
    for i, v in enumerate(x):
        assert v == out[i]


@raises(TypeError)
def test_set_forbidden_values_invalid_noniterable():
    leaf = Leaf()
    x = 9
    leaf.forbidden_values = x


# Test all correct ways to set validators and a few incorrect
# ones.

def test_undo_validators():
    leaf = Leaf()
    x = None
    leaf.validators = x
    assert x == leaf.validators


def test_set_validators():
    leaf = Leaf()
    avail_vals, nparams = leaf.available_validators()
    x = []
    for i, n in enumerate(nparams):
        if n == 1:
            x.append((avail_vals[i], random.random()))
        else:
            x.append((avail_vals[i],
                     [random.random(), random.random()]))
    leaf.validators = x
    out = leaf.validators
    assert isinstance(out, collections.Iterable)
    assert len(x) == len(out)
    for i, v in enumerate(x):
        assert isinstance(out[i], collections.Iterable)
        assert len(v) == len(out[i])
        assert v[0] == out[i][0]
        if not isinstance(v[1], collections.Iterable):
            assert v[1] == out[i][1]
        else:
            assert len(v[1]) == len(out[i][1])
            for i2, v2 in enumerate(v[1]):
                assert v2 == out[i][1][i2]


@raises(TypeError)
def test_set_validators_invalid_noniterable():
    leaf = Leaf()
    x = 9
    leaf.validators = x


@raises(TypeError)
def test_set_validators_invalid_not_iterable_of_iterables():
    leaf = Leaf()
    x = [1]
    leaf.validators = x


@raises(TypeError)
def test_set_validators_invalid_non2element_iterables():
    leaf = Leaf()
    x = [['LessThan']]
    leaf.validators = x


@raises(TypeError)
def test_set_validators_invalid_nonavailable_validator():
    leaf = Leaf()
    x = [['aivaanenfoaoefnaofve', 3]]
    leaf.validators = x


@raises(TypeError)
def test_set_validators_invalid_one_insteadof_two_parameters():
    leaf = Leaf()
    x = [['Between', 3]]
    leaf.validators = x


@raises(TypeError)
def test_set_validators_invalid_two_insteadof_one_parameter():
    leaf = Leaf()
    x = [['LessThan', [3, 2]]]
    leaf.validators = x


@raises(TypeError)
def test_set_validators_invalid_one__parameter_in_iterable():
    leaf = Leaf()
    x = [['LessThan', [3]]]
    leaf.validators = x


@raises(TypeError)
def test_set_validators_invalid_nonnumber_parameter():
    leaf = Leaf()
    x = [['LessThan', 'a']]
    leaf.validators = x


# Test all correct ways to set validator_function and a few incorrect
# ones.

def test_undo_validator_function():
    leaf = Leaf()
    x = None
    leaf.validator_function = x
    assert x == leaf.validator_function


def test_set_validator_function():
    leaf = Leaf()
    x = lambda y, z: True
    leaf.validator_function = x
    out = leaf.validator_function
    assert x == out


@raises(TypeError)
def test_set_validator_function_invalid_notfunction():
    leaf = Leaf()
    x = 9.2
    leaf.validator_function = x


@raises(TypeError)
def test_set_validator_function_invalid_wrongnumberargs():
    leaf = Leaf()
    x = lambda y, z, w: True
    leaf.validator_function = x


# Do tests on the Leaf's extra parameters abilities.

def test_extra_parameters_contains():
    leaf = Leaf(blah='3a', nd=4.2)
    assert 'blah' in leaf
    assert 'nd' in leaf
    assert 'somethingelse' not in leaf


def test_extra_parameters_get():
    leaf = Leaf(blah='3a', nd=4.2)
    assert '3a' == leaf['blah']
    assert 4.2 == leaf['nd']


def test_extra_parameters_set():
    leaf = Leaf()
    param = ('adfjadfka', 3934)
    leaf[param[0]] = param[1]
    assert param[0] in leaf
    assert param[1] == leaf[param[0]]


def test_extra_parameters_del():
    param = {'adfjadfka': 3934}
    leaf = Leaf(**param)
    assert list(param.keys())[0] in leaf
    del leaf[list(param.keys())[0]]
    assert list(param.keys())[0] not in leaf


def test_extra_parameters_len():
    leaf = Leaf(**rand_params)
    assert len(rand_params) == len(leaf)


def test_extra_parameters_values():
    leaf = Leaf(**rand_params)
    assert len(rand_params) == len(leaf)
    for k, v in rand_params.items():
        assert k in leaf
        assert v == leaf[k]


def test_extra_parameters_iteration():
    leaf = Leaf(**rand_params)
    assert len(rand_params) == len(leaf)
    for k in leaf:
        assert k in rand_params
        assert leaf[k] == rand_params[k]


def test_extra_parameters_keys():
    leaf = Leaf(**rand_params)
    assert set(rand_params.keys()) == set(leaf.keys())


def test_extra_parameters_items():
    leaf = Leaf(**rand_params)
    assert set(rand_params.items()) == set(leaf.items())

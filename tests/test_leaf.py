# Copyright (C) 2015-2016 Freja Nordsiek
#
# This package is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Tests for SettingsTree.Leaf. """

import posixpath
import random
import string
import collections

from nose.tools import raises

from SettingsTree import Leaf


random.seed()


# A of random set of parameters to use.
rand_params = dict()
ltrs = string.ascii_letters + string.digits
for i in range(random.randint(5, 10)):
    k = ''.join([random.choice(ltrs) for j in range(0, 20)])
    v = random.random()
    rand_params[k] = v

# A random group of settings to use.
settings = dict()
for i in range(5, 20):
    depth = random.randint(1, 6)
    path = '/'
    for j in range(0, depth):
        path = posixpath.join(path, \
            ''.join([random.choice(ltrs) \
            for j in range(0, random.randint(4, 9))]))
    settings[path] = random.random()


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


# Test initializing to a set value and setting the value.
def test_initialize_value():
    x = random.random()
    leaf = Leaf(value=x)
    assert x == leaf.value


def test_set_value():
    leaf = Leaf()
    x = random.random()
    leaf.value = x
    assert x == leaf.value


# Test all correct ways to set valid_value_types and a few incorrect
# ones.

def test_undo_valid_value_types():
    leaf = Leaf(valid_value_types=int)
    assert leaf.valid_value_types is not None
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
    leaf = Leaf(allowed_values=(3,))
    assert leaf.allowed_values is not None
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
    leaf = Leaf(forbidden_values=(3,))
    assert leaf.forbidden_values is not None
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
    leaf = Leaf(validators=[['LessThan', 2]])
    assert leaf.validators is not None
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


def test_set_validator_function():
    leaf = Leaf()
    x = lambda y, z: True
    leaf.validator_function = x
    out = leaf.validator_function
    assert x == out


def test_undo_validator_function():
    leaf = Leaf(validator_function=lambda y, z: True)
    assert leaf.validator_function is not None
    x = None
    leaf.validator_function = x
    assert x == leaf.validator_function


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


# Check the validity testing one test at a time.

def test_validation_notests():
    leaf = Leaf()
    leaf.value = random.random()
    assert leaf.is_valid(settings)


def test_validation_type_valid_single():
    leaf = Leaf(valid_value_types=float)
    leaf.value = random.random()
    assert leaf.is_valid(settings)


def test_validation_type_valid_multi():
    leaf = Leaf(valid_value_types=(float, int))
    leaf.value = random.random()
    assert leaf.is_valid(settings)


def test_validation_type_invalid_single():
    leaf = Leaf(valid_value_types=list)
    leaf.value = random.random()
    assert not leaf.is_valid(settings)


def test_validation_type_invalid_multi():
    leaf = Leaf(valid_value_types=(list, tuple))
    leaf.value = random.random()
    assert not leaf.is_valid(settings)


def test_validation_allowed_values_valid():
    leaf = Leaf()
    x = [random.random() for i in range(5, 10)]
    leaf.allowed_values = x
    leaf.value = x[random.randrange(len(x))]
    assert leaf.is_valid(settings)


def test_validation_allowed_values_invalid():
    leaf = Leaf()
    x = [random.random() for i in range(5, 10)]
    leaf.allowed_values = x
    y = x[0]
    while y in x:
        y = random.random()
    leaf.value = y
    assert not leaf.is_valid(settings)


def test_validation_forbidden_values_valid():
    leaf = Leaf()
    x = [random.random() for i in range(5, 10)]
    leaf.forbidden_values = x
    y = x[0]
    while y in x:
        y = random.random()
    leaf.value = y
    assert leaf.is_valid(settings)


def test_validation_forbidden_values_invalid():
    leaf = Leaf()
    x = [random.random() for i in range(5, 10)]
    leaf.forbidden_values = x
    leaf.value = x[random.randrange(len(x))]
    assert not leaf.is_valid(settings)


def test_validation_validators_GreaterThan_valid():
    leaf = Leaf()
    validators = [['GreaterThan', random.random()]]
    leaf.validators = validators
    for i in range(100):
        leaf.value = validators[0][1] + 100.0 * random.random()
        assert leaf.is_valid(settings)


def test_validation_validators_GreaterThan_invalid():
    leaf = Leaf()
    validators = [['GreaterThan', random.random()]]
    leaf.validators = validators
    leaf.value = validators[0][1]
    assert not leaf.is_valid(settings)
    for i in range(100):
        leaf.value = validators[0][1] - 100.0 * random.random()
        assert not leaf.is_valid(settings)


def test_validation_validators_GreaterThanOrEqualTo_valid():
    leaf = Leaf()
    validators = [['GreaterThanOrEqualTo', random.random()]]
    leaf.validators = validators
    leaf.value = validators[0][1]
    assert leaf.is_valid(settings)
    for i in range(100):
        leaf.value = validators[0][1] + 100.0 * random.random()
        assert leaf.is_valid(settings)


def test_validation_validators_GreaterThanOrEqualTo_invalid():
    leaf = Leaf()
    validators = [['GreaterThanOrEqualTo', random.random()]]
    leaf.validators = validators
    for i in range(100):
        leaf.value = validators[0][1] - 100.0 * random.random()
        assert not leaf.is_valid(settings)


def test_validation_validators_LessThan_valid():
    leaf = Leaf()
    validators = [['LessThan', random.random()]]
    leaf.validators = validators
    for i in range(100):
        leaf.value = validators[0][1] - 100.0 * random.random()
        assert leaf.is_valid(settings)


def test_validation_validators_LessThan_invalid():
    leaf = Leaf()
    validators = [['LessThan', random.random()]]
    leaf.validators = validators
    leaf.value = validators[0][1]
    assert not leaf.is_valid(settings)
    for i in range(100):
        leaf.value = validators[0][1] + 100.0 * random.random()
        assert not leaf.is_valid(settings)


def test_validation_validators_LessThanOrEqualTo_valid():
    leaf = Leaf()
    validators = [['LessThanOrEqualTo', random.random()]]
    leaf.validators = validators
    leaf.value = validators[0][1]
    assert leaf.is_valid(settings)
    for i in range(100):
        leaf.value = validators[0][1] - 100.0 * random.random()
        assert leaf.is_valid(settings)


def test_validation_validators_LessThanOrEqualTo_invalid():
    leaf = Leaf()
    validators = [['LessThanOrEqualTo', random.random()]]
    leaf.validators = validators
    for i in range(100):
        leaf.value = validators[0][1] + 100.0 * random.random()
        assert not leaf.is_valid(settings)


def test_validation_validators_NotEqual_valid():
    leaf = Leaf()
    validators = [['NotEqual', random.random()]]
    leaf.validators = validators
    x = set([random.random() for i in range(100)])
    for v in x:
        leaf.value = v
        assert leaf.is_valid(settings)


def test_validation_validators_NotEqual_invalid():
    leaf = Leaf()
    validators = [['NotEqual', random.random()]]
    leaf.validators = validators
    leaf.value = validators[0][1]
    assert not leaf.is_valid(settings)


def test_validation_validators_Between_valid():
    leaf = Leaf()
    bounds = sorted([random.random(), random.random()])
    validators = [['Between', bounds]]
    leaf.validators = validators
    x = bounds + [random.uniform(*bounds) for i in range(100)]
    for v in x:
        leaf.value = v
        assert leaf.is_valid(settings)


def test_validation_validators_Between_invalid():
    leaf = Leaf()
    bounds = sorted([random.random(), random.random()])
    validators = [['Between', bounds]]
    leaf.validators = validators
    x = [min(bounds) - 100.0 * random.random()  for i in range(100)] \
        + [max(bounds) + 100.0 * random.random()  for i in range(100)]
    for v in x:
        leaf.value = v
        assert not leaf.is_valid(settings)


def test_validation_validators_BetweenNotInclusive_invalid_bounds():
    leaf = Leaf()
    bounds = sorted([random.random(), random.random()])
    validators = [['Between', bounds], ['NotEqual', bounds[0]],
                  ['NotEqual', bounds[1]]]
    leaf.validators = validators
    for v in bounds:
        leaf.value = v
        assert not leaf.is_valid(settings)


def test_validation_validators_NotBetween_invalid():
    leaf = Leaf()
    bounds = sorted([random.random(), random.random()])
    validators = [['NotBetween', bounds]]
    leaf.validators = validators
    x = [min(bounds) - 100.0 * random.random()  for i in range(100)] \
        + [max(bounds) + 100.0 * random.random()  for i in range(100)] \
        + bounds
    for v in x:
        leaf.value = v
        assert leaf.is_valid(settings)


def test_validation_validators_NotBetween_valid():
    leaf = Leaf()
    bounds = sorted([random.random(), random.random()])
    validators = [['NotBetween', bounds]]
    leaf.validators = validators
    x = set([random.uniform(*bounds) for i in range(100)]) - set(bounds)
    for v in x:
        leaf.value = v
        assert not leaf.is_valid(settings)


def test_validation_validator_function_valid_alwaystrue():
    leaf = Leaf()
    leaf.validator_function = lambda x, y: True
    x = [random.random() for i in range(10)] + [list, 'av', [3]]
    for v in x:
        leaf.value = v
        assert leaf.is_valid(settings)


def test_validation_validator_function_valid_equalsetting():
    leaf = Leaf()
    name = random.choice(tuple(settings.keys()))
    leaf.validator_function = lambda x, y: x == y[name]
    leaf.value = settings[name]
    assert leaf.is_valid(settings)


def test_validation_validator_function_invalid_notequalsetting():
    leaf = Leaf()
    name = random.choice(tuple(settings.keys()))
    leaf.validator_function = lambda x, y: x == y[name]
    x = set([random.random() for i in range(100)]) - {settings[name]}
    for v in x:
        leaf.value = x
        assert not leaf.is_valid(settings)


def test_validation_validator_function_invalid_alwaysfalse():
    leaf = Leaf()
    leaf.validator_function = lambda x, y: False
    x = [random.random() for i in range(10)] + [list, 'av', [3]]
    for v in x:
        leaf.value = v
        assert not leaf.is_valid(settings)


def test_validation_validator_function_invalid_exception():
    leaf = Leaf()
    
    def fun(x, y):
        raise TypeError('blah')
    
    leaf.validator_function = fun
    x = [random.random() for i in range(10)] + [list, 'av', [3]]
    for v in x:
        leaf.value = v
        assert not leaf.is_valid(settings)


def test_validation_mixed_invalid_alwaysfalse_butallowed():
    leaf = Leaf()
    x = random.random()
    leaf.validator_function = lambda x, y: False
    leaf.allowed_values = [x]
    leaf.value = x
    assert not leaf.is_valid(settings)


def test_validation_mixed_invalid_alwaystrue_butforbidden():
    leaf = Leaf()
    x = random.random()
    leaf.validator_function = lambda x, y: True
    leaf.forbidden_values = [x]
    leaf.value = x
    assert not leaf.is_valid(settings)


def test_validation_mixed_invalid_allowedvalue_butwrongtype():
    leaf = Leaf()
    x = random.randrange(100)
    leaf.valid_value_types = float
    leaf.allowed_values = [x]
    leaf.value = x
    assert not leaf.is_valid(settings)

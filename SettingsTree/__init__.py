# Copyright (c) 2013-2015, Freja Nordsiek
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

""" Module for reading/writing/displaying/editing settings trees.

Version 0.3

"""

__version__ = "0.3"

import copy
import posixpath
import itertools
import collections
import numbers
import inspect


class Leaf(object):
    """ An individual setting.

    A setting that is part of a nested tree of settings (see ``Tree``),
    has a value (``value``), and possibly requires validation checks.

    A setting is valid if it meets several criteria. Note, it is
    possible to set the criteria such that it can never be valid with
    any value. It is valid (call ``is_valid``) if it meets all the
    following criteria.

    1. It's type is one of the types contained in ``valid_value_types``,
       if given.
    2. It is one of the values in ``allowed_values``, if given.
    3. It is not one of the values in ``forbidden_values``, if given.
    4. It passes all the simple validators in ``validators``, if given.
       See ``available_validators`` for the available ones and how to
       set their parameters. More than one can be used in combination.
       They are meant for numerical settings to make sure they are
       less than a value, greater than, in a range, outside a range,
       etc.
    5. It passes the custom validation function provided
       (``validator_function``), if given. It must be a function
       (includes those made by ``lambda``). It must return a ``bool``
       indicating whether the setting is valid (``True``) or not
       (``False``) and take two arguments. The first is the value of
       this setting and the second is a ``dict`` containing all the
       other settings in the root settings ``Tree`` that this is a part
       of with the POSIX paths to the individual setting leaves as the
       keys and their values as the values. Thowing an exception, which
       will be caught, is considered as the setting being invalid.

    Additional parameters can be stored in this ``Leaf`` and accessed
    like a ``dict``. The initial ones are set by `**keywords`, but then
    can be set and gotten by the usual ways of working with a ``dict``
    such as ``leaf['a']``.

    Parameters
    ----------
    value : any, optional
        The value of this setting. See Attributes.
    valid_value_types : type, iterable of types, optional
        See Attributes.
    allowed_values : iterable, optional
        See Attributes.
    forbidden_values : iterable, optional
        See Attributes.
    validators : iterable of iterables, optional
        See Attributes.
    validator_function : function, optional
        See Attributes.
    **keywords : optional
        Aditional keyword arguments which are put in this ``Leaf`` to
        be accessed by accessing this ``Leaf`` like a ``dict``.

    Raises
    ------
    TypeError
        If set to something invalid.

    Attributes
    ----------
    value : any type
    valid_value_types : iterable of classes or None
    allowed_values : iterable or None
    forbidden_values : iterable or None
    validators : iterable of iterables or None
    validator_function : function or None

    See Also
    --------
    Tree
    available_validators

    """
    def __init__(self, value=None, valid_value_types=None,
                 allowed_values=None, forbidden_values=None,
                 validators=None, validator_function=None,
                 **keywords):
        # The value is set without question.
        self.value = value
        
        # For the others, the values to set need to be validated. So,
        # they are all set to None, which is a valid value, and then one
        # by one set to the given values.
        self._validator_function = None
        self._valid_value_types = None
        self._allowed_values = None
        self._forbidden_values = None
        self._validators = None
        
        self.validator_function = validator_function
        self.valid_value_types = valid_value_types
        self.allowed_values = allowed_values
        self.forbidden_values = forbidden_values
        self.validators = validators

        # Copy everything in keywords into the extra parameters
        # dictionary.
        self._extra_parameters = copy.deepcopy(keywords)

    @property
    def value(self):
        """ The value of this particular setting

        any type

        See Also
        --------
        is_valid
        
        """
        return copy.deepcopy(self._value)

    @value.setter
    def value(self, value2):
        self._value = copy.deepcopy(value2)


    @property
    def valid_value_types(self):
        """ The python types that the setting value must be a type of.

        type, iterable of types, or None

        The type/s that this setting's value must be a type of in
        order to be valid. ``None`` is used to indicate that any type
        is allowed. Is stored as ``None`` or a ``tuple`` of types.

        Raises
        ------
        TypeError
            If set to something invalid.

        """
        return copy.deepcopy(self._valid_value_types)
    
    @valid_value_types.setter
    def valid_value_types(self, value2):
        if value2 is None:
            self._valid_value_types = None
        elif isinstance(value2, type):
            self._valid_value_types = (value2,)
        elif isinstance(value2, collections.Iterable):
            for v in value2:
                if not isinstance(v, type):
                    raise TypeError('An element of the iterable was not'
                                    ' a type.')
            self._valid_value_types = tuple(value2)
        else:
            raise TypeError('Set to something invalid.')

    
    @property
    def allowed_values(self):
        """ The allowed setting values.

        iterable or None

        The valid values allowed for this setting. ``None`` designates
        that this feature is not used (all values otherwise valid
        are allowed). Stored as ``None`` or a ``tuple``.

        Raises
        ------
        TypeError
            If set to something invalid.

        See Also
        --------
        forbidden_values
        
        """
        return copy.deepcopy(self._allowed_values)

    @allowed_values.setter
    def allowed_values(self, value2):
        if value2 is None:
            self._allowed_values = None
        elif isinstance(value2, collections.Iterable):
            self._allowed_values = tuple(copy.deepcopy(value2))
        else:
            raise TypeError('Set to something invalid.')

    
    @property
    def forbidden_values(self):
        """ The forbidden setting values.

        iterable or None

        The values forbidden for this setting. ``None`` designates
        that this feature is not used. Stored as ``None`` or a ``tuple``.

        Raises
        ------
        TypeError
            If set to something invalid.

        See Also
        --------
        allowed_values
        
        """
        return copy.deepcopy(self._forbidden_values)

    @forbidden_values.setter
    def forbidden_values(self, value2):
        if value2 is None:
            self._forbidden_values = None
        elif isinstance(value2, collections.Iterable):
            self._forbidden_values = tuple(copy.deepcopy(value2))
        else:
            raise TypeError('Set to something invalid.')


    @property
    def validators(self):
        """ The simple validators to use and their parameters.
        
        iterable of iterables, or None

        The simple validators for the setting value to use and their
        parameters, or ``None`` to not use any. The available ones and
        how many parameters they required can be found by calling
        ``available_validators``. Each one must be given as a two
        element iterable with the string name of the simple validator
        in the first element and the parameters in the second. If it
        takes one parameter, the second element should be that
        parameter. If it takes two parameters, the second element
        should be an iterable of the two parameters. The parameters
        must inherit from ``numbers.Number``. The simple validators must
        be given as an iterable of them, so an iterable of iterables.

        Warning
        -------
        It is possible to set the group of simple validators such that
        no setting is valid.

        Raises
        ------
        TypeError
            If set to something invalid.

        See Also
        --------
        available_validators
        
        """
        return copy.deepcopy(self._validators)
    
    @validators.setter
    def validators(self, value2):
        if value2 is None:
            self._validators = None
        elif not isinstance(value2, collections.Iterable):
            raise TypeError('Must be set to an iterable of iterables.')
        else:
            # Check every simple validator to see if it is available
            # and the parameters match up.
            avail_vals, nparams = self.available_validators()
            for v in value2:
                if not isinstance(v, collections.Iterable) \
                        or len(v) != 2 or v[0] not in avail_vals:
                    raise TypeError('Each element must be a 2 element'
                                    ' iterable with an available'
                                    ' simple validator.')
                # If one parameter, it must be a number. If two
                # parameters it must be an iterable of two numbers.
                if 1 == nparams[avail_vals.index(v[0])]:
                    if not isinstance(v[1], numbers.Number):
                        raise TypeError('Parameter must be a Number')
                else:
                    if not isinstance(v[1], collections.Iterable) \
                            or len(v[1]) != 2 \
                            or not isinstance(v[1][0], numbers.Number) \
                            or not isinstance(v[1][1], numbers.Number):
                        raise TypeError('Parameters must be an '
                                        'iterable of two Numbers')
            # It is valid. Now assign it.
            self._validators = tuple([(v[0], copy.deepcopy(v[1]))
                                     for v in value2])


    @property
    def validator_function(self):
        """ Custom validation function to validate the setting.
        
        function or None

        User provided custom validator function to check the validity
        of this setting after all other checks have been done. ``None``
        means the feature is not used. It must be a function (includes
        those made by ``lambda``). It must return a ``bool`` indicating
        whether the setting is valid (``True``) or not (``False``) and
        take two arguments. The first is the value of this setting
        and the second is a ``dict`` containing all the other
        settings in the root settings ``Tree`` that this is a part of
        with the POSIX paths to the individual setting leaves as the
        keys and their values as the values. Thowing an exception, which
        will be caught, is considered as the setting being invalid.

        Raises
        ------
        TypeError
            If set to something invalid.

        See Also
        --------
        Tree.list

        """
        return self._validator_function
    
    @validator_function.setter
    def validator_function(self, value2):
        if value2 is None:
            self._validator_function = None
        elif inspect.isfunction(value2) \
                and 2 == len(inspect.getargspec(value2).args):
            self._validator_function = copy.deepcopy(value2)
        else:
            raise TypeError('Must be set to a function taking 2 '
                            'arguments or None.')

    def available_validators(self):
        """ Returns the available validators and number of parameters.

        Returns the ``str`` identifiers for the simple validators that
        are available as well as the number of parameters each take.
        The available validators are in the table below for convenience.
        N is the number of parameters it takes. V is the value of this
        setting. X is the first (or only) parameter and Y is the
        second.

        ==========================  =  ================================
        validator                   N  Valid if
        ==========================  =  ================================
        ``'GreaterThan'``           1  V > X
        ``'LessThan'``              1  V < X
        ``'GreaterThanOrEqualTo'``  1  V >= X
        ``'LessThanOrEqualTo'``     1  V <= X
        ``'NotEqual'``              1  V != X
        ``'Between'``               2  min(X, Y) <= V <= max(X, Y)
        ``'NotBetween'``            2  V <= min(X, Y) OR V >= max(X, Y)
        ==========================  =  ================================

        Returns
        -------
        available_validators : tuple of str
            The names of the validators (first column in above table).
        number_parameters : tuple of ints
            The number of parameters each validator takes (second
            column in the above table).

        See Also
        --------
        validators
        
        """
        return (('GreaterThan', 'GreaterThanOrEqualTo', 'LessThan',
                'LessThanOrEqualTo', 'Between', 'NotBetween',
                'NotEqual'), (1, 1, 1, 1, 2, 2, 1))

    def is_valid(self, all_settings):
        """ Checks and returns whether this setting is valid or not.

        Parameters
        ----------
        all_settings : dict
            All the settings from the root ``Tree`` all the way to each
            end ``Leaf``. The keys are the POSIX paths to each ``Leaf``
            and the key is the value of the setting of the ``Leaf``.
            Generated by calling ``Tree.list()`` on the root ``Tree``.

        Returns
        -------
        validity : bool
            Whether this setting is valid (``True``) or not (``False``).

        See Also
        --------
        Tree.list
        
        """
        # Check that it is one of the allowed types, is an allowed
        # value, and is not a forbidden value.
        if self._valid_value_types is not None \
                and type(self._value) not in self._valid_value_types:
            return False
        if self._allowed_values is not None \
                and self._value not in self._allowed_values:
            return False
        if self._forbidden_values is not None \
                and self._value in self._forbidden_values:
            return False

        # Check the value against all the simple validators. First,
        # though, construct functions for the validators (true if
        # valid and false otherwise).
        vals = {'GreaterThan': lambda v, params: v > params,
                'LessThan': lambda v, params: v < params,
                'GreaterThanOrEqualTo': lambda v, params: v >= params,
                'LessThanOrEqualTo': lambda v, params: v <= params,
                'NotEqual': lambda v, params: v != params,
                'Between': lambda v, params: v >= min(params)
                and v <= max(params),
                'NotBetween': lambda v, params: v <= min(params)
                or v >= max(params)}
        if self._validators is not None:
            for val, params in self._validators:
                if not vals[val](self._value, params):
                    return False

        # Check the custom validator.
        if self._validator_function is not None:
            try:
                return self._validator_function(self._value,
                                                all_settings)
            except:
                return False

        # Must be valid since all tests were passed.
        return True

    # Implement a dictionary interface for all the extra parameters
    # by mapping the relevant dict functions to the functions inside
    # _extra_parameters.
    def __len__(self):
        """ Returns the number of extra parameters."""
        return len(self._extra_parameters)
    
    def __getitem__(self, key):
        """ Gets a particular extra parameter."""
        return self._extra_parameters[key]
    
    def __setitem__(self, key, value):
        """ Sets a particular extra parameter."""
        self._extra_parameters[key] = value
    
    def __delitem__(self, key):
        """ Removes a particular extra parameter."""
        del self._extra_parameters[key]
    
    def __contains__(self, item):
        """ Checks if a key is in the extra parameters."""
        return self._extra_parameters.__contains__(item)
    
    def __iter__(self):
        """ Returns an iterator over the extra parameters."""
        return self._extra_parameters.__iter__()
    
    def keys(self):
        """ Returns all the keys for the extra parameters."""
        return self._extra_parameters.keys()
    
    def items(self):
        """ Returns the items of the extra parameters."""
        return self._extra_parameters.items()


class Tree(object):
    """ Object to work with a tree of settings.

    Represents a tree of settings composed of one or more ``Tree`` that
    can be nested and then one or more ``Leaf`` objects as the settings
    themselves. The children of this ``Tree`` are ordered by the order
    that each ``Tree`` and ``Leaf`` are added.

    Parameters
    ----------
    children : anything that inherits collections.Mapping, optional
        A ``dict`` or ``dict`` like object (inherits from
        ``collections.Mapping``) of one or more ``Tree`` and/or
        ``Leaf`` to be put into this ``Tree``. They are added in order
        that `children` is mapped. Each key is a POSIX path to where to
        put the ``Leaf`` or ``Tree`` associated with it.
    **keywords : optional
        Aditional keyword arguments which are put in this ``Tree``.

    Raises
    ------
    TypeError
        If set to something invalid.

    Notes
    -----
    Recursion is used very heavily in this class for all operations, so
    the tree of settings should not be nested too deep.

    See Also
    --------
    Leaf
    collections.Mapping

    """
    def __init__(self, children=None, **keywords):
        # Set _children to an empty ordered dict and then add the
        # elements of children one by one if it is dict like
        self._children = collections.OrderedDict()
        if children is not None:
            if not isinstance(children, collections.Mapping):
                raise TypeError('children must be a Mapping of '
                                + 'Tree''s and Leaf''s.')
            for k, v in children.items():
                if isinstance(v, (Tree, Leaf)):
                    self[k] = v
                else:
                    raise TypeError('children must be a Mapping of '
                                    + 'Tree''s and Leaf''s.')

        # Copy everything in keywords into the extra parameters
        # dictionary.
        self._extra_parameters = copy.deepcopy(keywords)


    # Implement a dictionary interface for all the chilren.

    def __len__(self):
        """ Returns the number of children in this Tree."""
        return len(self._children)

    def __contains__(self, item):
        """ Checks if a key is in one of the children."""
        try:
            junk = self[item]
        except:
            return False
        else:
            return True

    def __iter__(self):
        """ Returns an iterator over the children."""
        return self._children.__iter__()

    def keys(self):
        """ Returns all the keys for the children."""
        return self._children.keys()

    def items(self):
        """ Returns all the children and their names in this Tree."""
        return self._children.items()

    def __getitem__(self, path):
        """ Gets by path.

        Gets by a POSIX style path. Each subdirectory in the path is a
        ``Tree`` that holds one or more ``Tree`` and/or ``Leaf``. The
        file part accesses the particular ``Leaf`` or ``Tree``. In all
        cases, if a ``Leaf`` is reached in the path and there is more
        path after that, then the rest references an extra parameter in
        that ``Leaf``. The value of the ``Leaf`` or ``list`` of the
        children of the ``Tree`` is obtained if the path does not end in
        a trailing ``'/'``. If a trailing ``'/'`` is present, then the
        ``Leaf`` or ``Tree`` pointed to by `path` is returned.

        Parameters
        ----------
        path : str
            POSIX style path to the desired setting. ``'/'`` is the root
            of this ``Tree``. A trailing ``'/'`` means return the Leaf
            or Tree pointed to by `path` instead of its value
            (``Leaf``) or a ``list`` of its children (``Tree``).

        Returns
        -------
        value: Tree or Leaf or value or list of str, optional
            The ``Leaf`` or ``Tree`` pointed to, the value of the
            ``Leaf``, or a ``list`` of the children of the ``Tree``.

        Raises
        ------
        KeyError
            If the setting pointed to by `path` cannot be found.

        See Also
        --------
        posixpath
        Leaf.value

        """
        return self._getsetdel_item(path, 'get')

    def __setitem__(self, path, value):
        """ Sets by path.

        Gets, sets, or deletes by a POSIX style path. Each subdirectory
        in the path is a ``Tree`` that holds one or more ``Tree`` and/or
        ``Leaf``. The file part accesses the particular ``Leaf`` or
        ``Tree``. In all cases, if a ``Leaf`` is reached in the path and
        there is more path after that, then the rest references an extra
        parameter in that ``Leaf`` which will be set to `value`. If
        `value` is a ``Tree`` or ``Leaf``, then the location pointed to
        by `path` is set to `value`. Otherwise, `path` must point to a
        ``Leaf``, in which case its value is set to `leaf`.

        Parameters
        ----------
        path : str
            POSIX style path to the desired setting. ``'/'`` is the root
            of this ``Tree``. A trailing ``'/'`` has no effect unless
            we are doing a get 'operation' in which case its presence
            means return the Leaf or Tree pointed to by `path` instead
            of its value (``Leaf``) or a ``list`` of its children
            (``Tree``).
        operation : {'get', 'set', 'del'}
            Whether to get, set, or delete.
        value : Tree or Leaf or value, optional
            The value to set. If it is a ``Tree`` or ``Leaf``, then
            `path` points to the desired name for it. Otherwise, it is a
            value and `path` must point to a ``Leaf`` which will have
            its value set to `value`.

        Raises
        ------
        KeyError
            If the setting pointed to by `path` cannot be found.
        TypeError
            If trying to set a ``Tree`` to not a ``Tree`` or ``Leaf``.

        See Also
        --------
        posixpath
        Leaf.value

        """
        self._getsetdel_item(path, 'set', value=value)

    def __delitem__(self, path):
        """ Gets, sets, or deletes by path.

        Gets, sets, or deletes by a POSIX style path. Each subdirectory
        in the path is a ``Tree`` that holds one or more ``Tree`` and/or
        ``Leaf``. The file part accesses the particular ``Leaf`` or
        ``Tree``. In all cases, if a ``Leaf`` is reached in the path and
        there is more path after that, then the rest references an extra
        parameter in that ``Leaf``. The ``Leaf``, ``Tree``, or ``Leaf``
        extra parameter pointed to by `path` is deleted.

        Parameters
        ----------
        path : str
            POSIX style path to the desired setting.

        Raises
        ------
        KeyError
            If the setting pointed to by `path` cannot be found.

        See Also
        --------
        posixpath
        Leaf.value

        """
        self._getsetdel_item(path, 'del')

    def _getsetdel_item(self, path, operation, value=None):
        """ Gets, sets, or deletes by path.

        Gets, sets, or deletes by a POSIX style path. Each subdirectory
        in the path is a ``Tree`` that holds one or more ``Tree`` and/or
        ``Leaf``. The file part accesses the particular ``Leaf`` or
        ``Tree``. In all cases, if a ``Leaf`` is reached in the path and
        there is more path after that, then the rest references an extra
        parameter in that ``Leaf``.

        If doing a get `operation`, the value of the ``Leaf`` or
        ``list`` of the children of the ``Tree`` is obtained if the path
        does not end in a trailing ``'/'``. If a trailing ``'/'`` is
        present, then the ``Leaf`` or ``Tree`` pointed to by `path` is
        returned.

        If doing a set `operation` and `value` is a ``Tree`` or
        ``Leaf``, then the location pointed to by `path` is set to
        `value` even if parent ``Tree`` need to be made. Otherwise,
        `path` must point to a ``Leaf``, in which case its value is set
        to `leaf`.

        If doing a del `operation`, the ``Leaf`` or ``Tree`` pointed to
        by `path` is deleted.

        Parameters
        ----------
        path : str
            POSIX style path to the desired setting. ``'/'`` is the root
            of this ``Tree``. A trailing ``'/'`` has no effect unless
            we are doing a get 'operation' in which case its presence
            means return the Leaf or Tree pointed to by `path` instead
            of its value (``Leaf``) or a ``list`` of its children
            (``Tree``).
        operation : {'get', 'set', 'del'}
            Whether to get, set, or delete.
        value : Tree or Leaf or value, optional
            When doing a set `operation`, the value to set. If it is a
            ``Tree`` or ``Leaf``, then `path` points to the desired name
            for it. Otherwise, it is a value and `path` must point to a
            ``Leaf`` which will have its value set to `value`.

        Returns
        -------
        value: Tree or Leaf or value or list of str, optional
            If doing a get `operation`, the ``Leaf`` or ``Tree``
            pointed to, the value of the ``Leaf``, or a ``list`` of
            the children of the ``Tree``.

        Raises
        ------
        KeyError
            If the setting pointed to by `path` cannot be found.
        ValueError
            `operation` is not one of the allowed operations.
        TypeError
            If trying to set a ``Tree`` to not a ``Tree`` or ``Leaf``.

        See Also
        --------
        posixpath
        Leaf.value

        """
        # Check that operation is one of the allowed values.
        if operation not in ('get', 'set', 'del'):
            raise ValueError('operation must be ''get'', ''set'', '
                             + 'or ''del''.')

        # If operation is get and path is just '/', then return this
        # Tree. If it is two in a row, return the list of all
        # children.
        if operation == 'get':
            if path == 2 * posixpath.sep:
                return self
            elif path == posixpath.sep:
                return list(self._children.keys())

        # Sanitize the path normalizing out '../' and stuff.
        spath = posixpath.normpath(path)

        # '/' isn't allowed for set and del
        if operation in ('set', 'del') \
                and spath.count(posixpath.sep) == len(spath):
            raise KeyError('Can''t set or del root Tree.')

        # Remove the leading '/'s if it is an absolute path.
        while spath[0] == posixpath.sep:
            spath = spath[1:]

        # Now, the sanitizing would have removed any trailing '/', so
        # one needs to be put back on if there was one and we are doing
        # a get.
        if operation == 'get' and path[-1] == posixpath.sep:
            spath = spath + posixpath.sep

        # Find the position of the first separator.
        index = spath.find(posixpath.sep)

        # The case of no separator, a trailing separator, and a
        # separator in the middle all need to be handled separately.
        if index == -1:
            # As there was no separator, spath specifies the particular
            # setting that is wanted. For a get, it must be in the
            # Tree's children or it is an error. For a get, the value is
            # returned for a Leaf and the list of children returned for
            # a Tree. For a set, if value is a Tree or Leaf, then it is
            # set. If value is just a value, the Leaf's value will be
            # set if there is a Leaf there (otherwise an error is
            # thrown). If it is a del, it is deleted if present and an
            # error thrown if not.
            if operation == 'get':
                if spath not in self._children:
                    raise KeyError('Couldn''t find ' + spath + '.')
                elif isinstance(self._children[spath], Leaf):
                    return self._children[spath].value
                elif isinstance(self._children[spath], Tree):
                    return list(self._children[spath].keys())
                else:
                    raise KeyError(spath + ' is an invalid object.')
            else:
                if isinstance(value, (Leaf, Tree)):
                    self._children[spath] = value
                elif spath not in self._children:
                    raise KeyError('Couldn''t find ' + spath + '.')
                elif operation == 'del':
                    del self._children[spath]
                else:
                    if isinstance(self._children[spath], Tree):
                        raise TypeError('Can''t set a Tree to a value.')
                    elif isinstance(self._children[spath], Leaf):
                        self._children[spath].value = value
                    else:
                        raise KeyError(spath + ' is an invalid object.')

        elif index == len(spath) - 1:
            # This is a get (only way a trailing '/' is allowed) and the
            # separator is at the very end, meaning that the actual Tree
            # or Leaf is desired. If it is not in children, an error
            # must be raised.
            if spath[:-1] not in self._children:
                raise KeyError('Couldn''t find ' + spath + '.')
            else:
                return self._children[spath[:-1]]
        else:
            # The separator is in the middle, meaning that there is more
            # path after it. So, the part before and the part after need
            # to be obtained. If the part before is not in this Tree's
            # children, a Tree must be made if value is a Tree or Leaf
            # and we are doing a set operation and an error must be
            # riased otherwise. Otherwise, we need to recurse into that
            # Tree or Leaf (means the remainder of the path is an extra
            # parameter).
            rootpath = spath[:index]
            subpath = spath[(index + 1):]
            if rootpath not in self._children:
                if operation == 'set' \
                        and isinstance(value, (Tree, Leaf)):
                    self[rootpath] = Tree(children={subpath: value})
                else:
                    raise KeyError('Couldn''t find ' + rootpath + '.')
            elif isinstance(self._children[rootpath], (Tree, Leaf)):
                if operation == 'get':
                    return self._children[rootpath][subpath]
                elif operation == 'set':
                    self._children[rootpath][subpath] = value
                else:
                    del self._children[rootpath][subpath]
            else:
                raise KeyError(rootpath + ' is not a Tree or Leaf. '
                               'Only Trees and Leaves can hold '
                               + 'things.')

    def list_all(self, tp='all'):
        """ List the children of the Tree recursively.

        Returns the list of the POSIX paths to all the children of
        this ``Tree`` (including those nested within its children and
        their children and so on) of particular types (``Tree``,
        ``Leaf``, or all).

        Parameters
        ----------
        tp : {'all', 'tree', 'leaf'}, optional
            What kind of things to return the paths to: ``Tree``,
            ``Leaf``, or both ('all').

        Returns
        -------
        paths : list of str
            The paths to all the children at all depths of this ``Tree``
            of the desired types.

        Raises
        ------
        ValueError
            `tp` is not one of the valid values.

        """
        # Check the validity of tp.
        if tp not in ('all', 'tree', 'leaf'):
            raise ValueError('tp is not ''all'', ''tree'', or'
                             + ' ''leaf''.')

        # Iterate through each child and grab the paths to all desired
        # children that fit the type. For Trees, regardless of what type
        # we are collecting, we have to recurse into them and prepend the
        # name of the tree to the beginning (stripping the leading '/').
        children = []
        for k, v in self.items():
            if isinstance(v, Leaf):
                if tp != 'tree':
                    children.append(k)
            else:
                if tp != 'leaf':
                    children.append(k)
                children.extend([posixpath.join(k, pth[1:])
                                for pth in v.list_all(tp=tp)])

        # Prepend with a '/', sort them, and then return them.
        return sorted([posixpath.sep + ch for ch in children])

    def diff(self, tree):
        """ Find locations of differences between two ``Tree``.

        Compares the individual elements this ``Tree`` and the one
        provided (`tree`). The POSIX style paths to each ``Leaf``
        that is different between the two are returned in
        three lists. One list for those found in both, but had different
        values. The second for ones found in this ``Tree``, but not
        `tree`. And the third for ones found in `tree`, but not this
        ``Tree``.

        Parameters
        ----------
        tree : Tree
            The ``Tree`` to compare to.

        Returns
        -------
        different_values : list
            ``list`` of POSIX paths to each ``Leaf`` that is present in
            both trees, but have different values.
        only_in_self : list
            ``list`` of POSIX paths to each ``Leaf`` that is only
            present in this ``Tree`` (not in `tree`).
        only_in_other : list
            ``list`` of POSIX paths to each ``Leaf`` that is only
            present in `tree` (not in this ``Tree``).

        Raises
        ------
        TypeError
            If `tree` is not a ``Tree``.

        Examples
        --------

        A very simple ``Tree`` with three individual settings 'a',
        'b', and 'c' is made. Another tree is made by copying it,
        deleting 'b', changing the value of 'c', and adding another
        setting 'd'. Then they are compared.

        >>> import copy
        >>> tree1 = Tree(children={
                         'a': Leaf(value=2),
                         'b': Leaf(value=10.2),
                         'c': Leaf(value='foo')})
        >>> tree2 = copy.deepcopy(tree1)
        >>> del tree2['b']
        >>> tree2['c'] = 'bar'
        >>> tree2['d'] = Leaf(value=42)
        >>> tree1.diff(tree2)
        (['/c'], ['/b'], ['/d'])

        """
        # We must be given a Tree.
        if not isinstance(tree, Tree):
            raise TypeError('tree must be a Tree.')

        # Get the lists of all the leaves of both, which we
        # will need to compare them with, and pack them into sets (makes
        # it easier to figure out which are in both, and which are not).
        children = set(self.list_all(tp='leaf'))
        tree_children = set(tree.list_all(tp='leaf'))

        # Make lists for the leaves that are in one, or the other, or
        # both.
        only_in_self = list(children - tree_children)
        only_in_tree = list(tree_children - children)
        in_both = list(children & tree_children)

        # Sort the lists for convenience.
        only_in_self.sort()
        only_in_tree.sort()
        in_both.sort()

        # Take only those in both that have different values.
        different_values = list(itertools.filterfalse(lambda x:
                                self[x] == tree[x], in_both))

        return (different_values, only_in_self, only_in_tree)

    def find_invalids(self):
        """ Returns the paths to each invalid ``Leaf``.

        Goes through each ``Leaf`` in this ``Tree`` and any nested under
        it, checks their validity, and returns the POSIX paths to those
        that are invalid.

        Returns
        -------
        paths : list of str paths
            The POSIX paths to each invalid ``Leaf``.

        See Also
        --------
        is_valid
        Leaf.is_valid

        """
        # Get the paths to every Leaf and construct a dict of them with
        # the values of that particular leaf.
        leaves = dict([(k, self[k]) for k in self.list_all(tp='leaf')])

        # Check each leaf one by one for validity and gather those that
        # are invalid and return them.
        invalids = []
        for k in leaves:
            if not self[k + posixpath.sep].is_valid(leaves):
                invalids.append(k)
        return invalids

    def is_valid(self):
        """ Returns the paths to each invalid ``Leaf``.

        Goes through each ``Leaf`` in this ``Tree`` and any nested under
        it, checks their validity, and returns the POSIX paths to those
        that are invalid.

        Returns
        -------
        validity : bool
            ``True`` if every node is valid, and ``False`` otherwise.
        paths : list of str paths
            The POSIX paths to each invalid ``Leaf``.

        See Also
        --------
        find_invalids
        Leaf.is_valid

        """
        return (0 == len(self.find_invalids()))

    def get_values(self, form='paths'):
        """ Returns this ``Tree`` stripped just ``Leaf`` values.

        Parameters
        ----------
        form : {'paths', 'nested'}, optional
            Whether to return a ``dict`` of POSIX paths to ``Leaf``
            values (``'paths'``) or a group of nested ``dict``
            representing the structure of this ``Tree`` with a
            ``dict`` for each ``Tree`` and the values for each
            ``Leaf``.

        Returns
        -------
        output : dict
            A ``dict`` with elements determined by `form`. If `form`
            is ``'paths'``, then the POSIX paths to each ``Leaf`` will
            be the keys and the ``Leaf`` values as the values. If
            `form` is ``'nested'``, a group of nested ``dict`` is
            returned representing the structure of this ``Tree``.
            Each ``Tree`` is turned into a ``dict`` of its children
            which will be the respective values of each ``Leaf`` and
            another ``dict`` for each ``Tree``.

        Raises
        ------
        ValueError
            If `form` is not a valid value.

        See Also
        --------
        list_all
        set_values

        """
        if form == 'paths':
            # Get the paths to every Leaf and construct a dict of them
            # with the values of that particular leaf and return it.
            return dict([(k, self[k])
                        for k in self.list_all(tp='leaf')])
        elif form == 'nested':
            out = dict()
            for k, v in self.items():
                if isinstance(v, Leaf):
                    out[k] = v.value
                else:
                    out[k] = v.get_values(form=form)
            return out
        else:
            raise ValueError('form must be either ''paths'' or'
                             + ' ''nested''.')

    def set_values(self, values):
        """ Apply a group of values to several ``Leaf``.

        Sets several ``Leaf`` all at once. Skips any attempt to set the
        value of a ``Leaf`` that isn't present or set a ``Tree`` to a
        value that is not a ``dict`` of each ``Leaf`` to set within it
        (recursion).

        Parameters
        ----------
        values : dict or anything inheriting collections.Mapping
            Each key is a POSIX path to set and the value can either
            be a value to set a ``Leaf`` to if pointed at a ``Leaf``
            or a ``dict`` (or something that inherits
            ``collections.Mapping``) if pointing to a ``Tree`` in which
            case it takes the same form as `values` should. Basically,
            either output of ``get_values`` or mixed output form is
            what works.

        Raises
        ------
        TypeError
            If `values` doesn't inherit from ``collections.Mapping``.

        See Also
        --------
        get_values
        collections.Mapping

        """
        if not isinstance(values, collections.Mapping):
            raise TypeError('values must be dict-like (inherit from '
                            + 'collections.Mapping).')
        for k, v in values:
            if k in self:
                if isinstance(self[k], Leaf):
                    self[k].value = v
                elif isinstance(self[k], Tree):
                    if isinstance(v, dict):
                        self[k].set_values(v)

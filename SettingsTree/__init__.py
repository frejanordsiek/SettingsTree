# Copyright (c) 2013, Freja Nordsiek
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

Version 0.2

"""

__version__ = "0.2"

import copy
import posixpath
import itertools


class Tree(object):
    """ Object to work with a tree of settings.

    An object to maintain a tree of settings, extract its values
    (:py:func:`extract_values`), set all of its values
    (:py:func:`set_values`), check the validity of the values
    (:py:func:`check_values`), and read/write them from/to disk in JSON
    format.

    The validity of the optional supplied `tree` is not checked.

    Parameters
    ----------
    tree : dict, optional
        See Notes for format. Give ``None`` to get an empty
        parent. Note, it is not deep copied.

    Attributes
    ----------
    tree

    Notes
    -----
    `tree` is a ``dict`` representing the various settings to be
    read/written. Each element is a ``dict`` itself with a specific set
    of keys. If the element is a parent of other elements, a key
    named 'children' which contains a ``dict`` of all its children. If
    it is not a parent, the element represents a setting. It must then
    have keys named 'value' and 'validator'. 'value' is the element that
    holds the current value of the setting. 'validator' is a validation
    function that is called like  ``valid = validator(value, settings,
    child)`` which gives ``True`` if `value` is valid and ``False``
    otherwise given `tree` (it might depend on other settings) and
    the element of this particular setting (`child`). An element for a
    setting must not have a key named 'children'. The root node
    (`tree` itself) must be a parent node.

    Recursion is used very heavily in this class for all operations, so
    `tree` should not be nested too deep.

    """
    def __init__(self, tree=None):
        if isinstance(tree, dict):
            self._tree = tree
        else:
            self._tree = {'children': dict()}

        # Go through each node and set the 'path' field.
        self._tree['path'] = posixpath.sep
        self._set_paths(self._tree, posixpath.sep)

    @property
    def tree(self):
        """ Representation of the different settings.

        `tree` is a ``dict`` representing the various settings to be
        managed. See Notes for its format.

        Getting it just gets the reference as opposed to deep copying.

        Setting it extracts the values from what it is being set to and
        then applies them (see :py:func:`extract_values` and
        :py:func:`set_values`), as opposed to replacing `tree`.

        Notes
        -----
        Each element is a ``dict`` itself with a specific set of keys.
        If the element is a parent of other elements, then it should
        have a key named 'children' which contains a ``dict`` of all its
        children. If it is not a parent, the element represents a
        setting. It must then have keys named 'value' and
        'validator'. 'value' is the element that holds the current value
        of the setting. 'validator' is a validation function that is
        called like ``valid = validator(value, settings, child)`` which
        gives ``True`` if `value` is valid and ``False`` otherwise given
        `tree` (it might depend on other settings) and the element
        of this particular setting (`child`). An element for a setting
        must not have a key named 'children'. The root node (`tree`
        itself) must be a parent node.

        """
        return self._tree

    @tree.setter
    def tree(self, tree2):
        # Extract the values from the given tree2 and then apply
        # them.
        self.set_values(self._extract_values_node(tree2),
                        force=False)

    def find_invalids(self, path=posixpath.sep):
        """ Returns the paths of the invalid settings under a path.

        Goes through each subnode of of the node of ``tree``
        specified by the POSIX style path and checks whether it
        is valid or not. A list of the paths to the invalid ones is
        returned.

        Parameters
        ----------
        path : str
            POSIX style path to the desired setting. ``'/'`` is the root
            of ``tree``.

        Returns
        -------
        list of str paths
            The list of all the settings that are invalid, as POSIX
            paths.

        Raises
        ------
        KeyError
            If the setting pointed to by `path` cannot be found.

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        See Also
        --------
        check_values

        """
        return self._find_invalids_node(path)

    def check_values(self, path=posixpath.sep):
        """ Returns whether the setting values under a path are valid.

        Goes through each node of ``tree`` under `path` (POSIX
        style) and checks whether it is valid or not. It is only
        considered valid if every node is valid (right keys, values that
        are valid, etc.).

        Parameters
        ----------
        path : str
            POSIX style path to the desired setting. ``'/'`` is the root
            of ``tree``.

        Returns
        -------
        bool
            ``True`` if every node is valid, and ``False`` otherwise.

        Raises
        ------
        KeyError
            If the setting pointed to by `path` cannot be found.

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        See Also
        --------
        find_invalids

        """
        return (0 == len(self.find_invalids(path)))

    def extract_values(self):
        """ Returns the settings stripped down to just its values.

        Returns
        -------
        dict
            A ``dict`` with an element for each node in ``tree``.
            Parent nodes get turned into a ``dict`` with all their
            children nodes as elements. Setting nodes get reduced to
            being just their value (``name: value``).

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        """
        return self._extract_values_node(self._tree)

    def set_values(self, values, force=False):
        """ Apply a set of values to the settings.

        At the end, the end of applying the values, the validity of
        everything is checked (see :py:func:`check_values`). This is
        necessary since while each individual value can be passed
        through the appropriate validator, setting one particular
        setting can make other ones invalid, which can only be seen at
        the end. If `force` is ``True``, then the new values are applied
        regardless of validity. If it is ``False``, they are not applied
        if the resulting ``tree`` would be invalid. The validity of
        the ``tree`` that would result from applying `values` is
        returned, regardless of whether ``tree`` is actually changed
        or not.

        Parameters
        ----------
        values : dict
            A ``dict`` holding the setting value for each node in
            ``tree``. For a setting node, the element in `values` is
            just ``key: value``. For parent nodes in ``tree``, the
            element is a ``dict`` of all the children, which are then
            formatted the same way. Basically, this is the same format
            as the output of :py:meth:`extract_values`
        force : bool, optional
            Whether to write the values to ``tree`` or not if the
            resulting ``tree`` would be made invalid. The default is
            ``False``.

        Returns
        -------
        bool
            Whether the ``tree`` that would result from applying
            `values` is valid (``True``) or not (``False``)

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        """
        # Apply the values to a copy of tree so that it isn't
        # overwritten yet. Even if force is False, we will still force
        # write on the copy and just check the validity of everything at
        # the end (its possible to change one setting and then the
        # change of another makes it valid again if there are
        # dependencies).

        tree_copy = copy.deepcopy(self._tree)
        tree_copy = self._set_values_node(tree_copy, values, \
                    force=True)

        # Check the validity of the copy.
        invalids = self._find_invalids_node(tree_copy)
        validity = (0 == len(invalids))

        # If it is valid or we are force writing, overwrite tree. It
        # is done by using _set_values_node rather than just setting
        # _tree to tree_copy, because the former means that the
        # _tree object get overwritten and any external references
        # to it are broken (tree_copy is a deep copy, so it has a
        # different reference chain).

        if validity or force:
            self._tree = self._set_values_node(self._tree, \
                values, force=True)

        # Return the validity.

        return validity

    def get_setting_by_path(self, path):
        """ Grab a setting by path.

        Gets a setting by a POSIX style path.

        Parameters
        ----------
        path : str
            POSIX style path to the desired setting. ``'/'`` is the root
            of `node`. If a path ends in a ``'/'``, the setting node is
            retrieved regardless of whether it is a parent or not. If it
            doesn't end in a ``'/'``, the value is returned if it is not
            a parent, or a ``list`` of the children names if it is a
            parent.

        Returns
        -------
        node or value or list of str
            The setting node (or its value for a non-parent  or a
            ``list`` of the names of its children for a parent
            `path` didn't end in ``'/'``) pointed to by `path`.

        Raises
        ------
        KeyError
            If the setting pointed to by `path` cannot be found.

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        See Also
        --------
        set_setting_by_path

        """
        return self._get_setting_by_path_node(self._tree, path)

    def set_setting_by_path(self, path, value, force=False):
        """ Set a setting by path.

        Sets a setting (value or node depending) by a POSIX style
        path. The validity of the resulting ``tree`` is
        returned. Unless `value` is being forced (``force = True``), the
        old value is restored.

        Parameters
        ----------
        path : str
            POSIX style path to the desired setting. ``'/'`` is the root
            of ``tree``.
        force : bool, optional
            Whether to write the value to the setting or not if the
            resulting ``tree`` would be made invalid.

        Returns
        -------
        bool
            Whether the ``tree`` that would result from applying
            `value` is valid (``True``) or not (``False``).

        Raises
        ------
        KeyError
            If the setting pointed to by `path` cannot be found, or it
            it is not an actual setting, but a parent.

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        See Also
        --------
        get_setting_by_path

        """
        # If the given path doesn't end in a '/', we need to add
        # one. This needs to be done so that we will grab the actual
        # node for a setting as opposed to its value.
        if path[-1] != posixpath.sep:
            spath = path + posixpath.sep
        else:
            spath = path

        # Grab the node for the particular setting
        node =  self.get_setting_by_path(spath)

        # If it isn't an actual setting, raise an error.
        if 'value' not in node:
            raise KeyError(path + ' is not a setting.')

        # Grab the old value, just in case setting it to the new one
        # makes tree invalid.
        old_value = node['value']

        # Set the new value, and check validity (which will be
        # returned). If we are not forcing the value, set it back if it
        # invalid.
        node['value'] = value
        if self.check_values():
            return True
        else:
            if not force:
                node['value'] = old_value
            return False

    def list_children(self, path):
        """ List the children of a setting.

        Returns the list of children of a setting node specified by a
        POSIX style path.

        Parameters
        ----------
        path : str
            POSIX style path to the desired setting to list the children
            of. ``'/'`` is the root of ``tree``.

        Returns
        -------
        list of str
            The children of the node at `path`. It is ``[]`` if it is an
            individual setting node as opposed to a parent node.

        Raises
        ------
        KeyError
            If the setting pointed to by `path` cannot be found, or it
            it is not an actual setting, but a parent.

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        """
        # Get the parent node pointed to by path.
        node = self.get_setting_by_path(path)

        # If it isn't a dict, or is not a parent, return []. If it a
        # parent, return all the children names.
        if not isinstance(node, dict) or 'children' not in node \
                or not isinstance(node['children'], dict):
            return []
        else:
            return list(node['children'].keys())

    def list_all(self, path=posixpath.sep, tp='all'):
        """ List the children of a setting recursively.

        Returns the list of all the children of a setting node
        (including those nested within its children and their children
        and so on) of particular types (parents, settings, or all)
        specified by a POSIX style path.

        Parameters
        ----------
        path : str
            POSIX style path to the desired setting to list the children
            of. ``'/'`` is the root of ``tree``.
        tp : {'all', 'parent', 'setting', 'neither'}, optional
            What kind of settings to return: parents, settings, or both
            ('all'). 'neither' is a special value for things that are
            neither kind and shouldn't be there.

        Returns
        -------
        list of str
            The children of the node at `path` of the desired types. It
            is ``[]`` if it is an individual setting node as opposed to
            a parent node.

        Raises
        ------
        KeyError
            If the setting pointed to by `path` cannot be found, or it
            it is not an actual setting, but a parent.

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        """
        # Get the children of this node.
        children = [posixpath.join(path, x) for x in
                    self.list_children(path)]

        # Now, recurse through all the children and find their children
        # and append them to the list.
        for i in range(0, len(children)):
            child = self.get_setting_by_path(children[i]
                                             + posixpath.sep)
            children.extend(self.list_all(child['path']))

        # If we are only grabbing parents or settings, we need to go
        # through and filter out the unwanted kinds.
        if tp == 'parent' or tp == 'setting' or tp == 'neither':
            children = list(itertools.filterfalse( \
                lambda x: self.type_path(x) != tp, children))

        # Sort them and then return them.
        children.sort()
        return children

    def type_path(self, path):
        """ Determines the type pointed to by a path.

        Returns what type is pointed to by the given `path`, whether it
        is a parent, a setting, or neither. The path is POSIX style.

        Parameters
        ----------
        path : str
            POSIX style path to the desired setting to list the children
            of. ``'/'`` is the root of ``tree``.

        Returns
        -------
        str
            The type of the node at `path`, which can be either
            'parent', 'setting', or 'neither'.

        Raises
        ------
        KeyError
            If the setting pointed to by `path` cannot be found, or it
            it is not an actual setting, but a parent.

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        """
        # If the given path doesn't end in a '/', we need to add
        # one. This needs to be done so that we will grab the actual
        # node for a setting as opposed to its value.
        if path[-1] != posixpath.sep:
            spath = path + posixpath.sep
        else:
            spath = path

        # Grab the node pointed to by the path.
        node = self.get_setting_by_path(spath)

        # Find out what it is, and then return that.
        if 'children' in node and 'value' not in node:
            return 'parent'
        elif 'children' not in node and 'value' in node:
            return 'setting'
        else:
            return 'neither'

    def diff(self, tree_or_Tree):
        """ Find locations of differences between two settings trees.

        Compares the individual settings between this settings tree and
        the one provided. The POSIX style paths to all individual
        settings that are different between the two are returned in
        three lists. One list for the settings found in both, but had
        different values. The second for ones found in this settings,
        but not the provided one. And the third for ones found in the
        provided one, but not this one.

        Parameters
        ----------
        tree_or_Tree : dict of settings or Tree
            The settings tree to compare to. Must either be a
            ``Tree`` or a ``dict`` of settings that a
            ``Tree`` can be constructed from.

        Returns
        -------
        tuple of 3 lists
            Each ``list`` contains POSIX style paths to individuals
            settings which are different. The first one contains those
            that are present in both trees, but have different values.
            The second one is those that are in this tree, but not the
            provided one. The third one is those that are in the
            provided tree, but not this one.

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        Examples
        --------

        A very simple settings tree with three individual settings 'a',
        'b', and 'c' is made. Another tree is made by copying it,
        deleting 'b', changing the value of 'c', and adding another
        setting 'd'. Then they are compared.

        >>> import copy
        >>> tree1 = {'children': {
                         'a':{'value': 2}, 'b':{'value': 10.2},
                         'c':{'value': 'foo'}}}
        >>> tree2 = copy.deepcopy(tree1)
        >>> del tree2['children']['b']
        >>> tree2['children']['c']['value'] = 'bar'
        >>> tree2['children']['d'] = {'value': 42}
        >>> tree1
        {'children': {'a': {'value': 2},
          'b': {'value': 10.2},
          'c': {'value': 'foo'}}}
        >>> tree2
        {'children': {'a': {'value': 2},
          'c': {'value': 'bar'},
          'd': {'value': 42}}}
        >>> sio = Tree(tree1)
        >>> sio2 = Tree(tree2)
        >>> sio1.diff(sio2)
        (['/c'], ['/b'], ['/d'])

        """
        # If we are given a Tree, all is good. Otherwise we were
        # given a tree, so we need to make a Tree from it.
        if isinstance(tree_or_Tree, Tree):
            sio = tree_or_Tree
        else:
            sio = Tree(tree_or_Tree)

        # Get the lists of all setting type children of both, which we
        # will need to compare them with, and pack them into sets (makes
        # it easier to figure out which are in both, and which are not).
        children = set(self.list_all(tp='setting'))
        sio_children = set(sio.list_all(tp='setting'))

        # Make lists for the settings that are in one, or the other, or
        # both.
        in_self_only = list(children - sio_children)
        in_sio_only = list(sio_children - children)
        in_both = list(children & sio_children)

        # Sort the lists for convenience.
        in_self_only.sort()
        in_sio_only.sort()
        in_both.sort()

        # Take only those in both that have different values.
        different = list(itertools.filterfalse(lambda x:
                         self.get_setting_by_path(x)
                         == sio.get_setting_by_path(x), in_both))

        return (different, in_self_only, in_sio_only)

    def __getitem__(self, path):
        """ Alias to ``get_setting_by_path``.

        Alias giving dictionary like access to this object.

        See Also
        --------
        get_setting_by_path

        """
        return self.get_setting_by_path(path)

    def __setitem__(self, path, value):
        """ Alias to ``set_tree_by_path``.

        Alias giving dictionary like set access to this object. Calls
        ``set_settigns_by_path`` with ``force=False` so that the
        settings tree can't be made invalid by setting this value.

        See Also
        --------
        set_tree_by_path
        
        """
        return self.set_setting_by_path(path, value, force=False)

    def _set_paths(self, node, rootpath):
        """ Sets the 'path' field for all settings in a node.

        Goes through all the children of a node and sets their 'path'
        field properly.

        Parameters
        ----------
        node : dict of settings nodes
            `dict` of settings nodes. Must be a parent, but can contain
            parent and children nodes.
        rootpath : str
            POSIX style path to `node` with a trailing ``'/'``.

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        """
        # Find any children and then go through them one by one setting
        # their paths, and recursing into them if they are a parent.
        for name, child in node['children'].items():
            child['path'] = posixpath.join(rootpath, name)
            if 'children' in child:
                self._set_paths(child,
                                posixpath.join(rootpath, name)
                                + posixpath.sep)

    def _get_setting_by_path_node(self, node, path):
        """ Grab a setting in a node by path.

        Gets a setting (value or node depending) in a node by a POSIX
        style path.

        Parameters
        ----------
        node : dict of settings nodes
            `dict` of settings nodes. Must be a parent, but can contain
            parent and children nodes.
        path : str
            POSIX style path to the desired setting. ``'/'`` is the root
            of `node`. If a path ends in a ``'/'``, the setting node is
            retrieved regardless of whether it is a parent or not. If it
            doesn't end in a ``'/'``, the value is returned if it is not
            a parent, or a ``list`` of the children names if it is a
            parent.

        Returns
        -------
        node or value or list of str
            The setting node (or its value for a non-parent  or a
            ``list`` of the names of its children for a parent
            `path` didn't end in ``'/'``) pointed to by `path`.

        Raises
        ------
        KeyError
            If the setting pointed to by `path` cannot be found.

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        """
        # If path is just '/', then return node.
        if path == posixpath.sep:
            return node

        # If node is not a parent, then it can't be found.
        if 'children' not in node:
            raise KeyError('Node isn''t a parent.')

        # Sanitize the path normalizing out '../' and stuff.
        spath = posixpath.normpath(path)

        # Now, the sanitizing would have removed any trailing '/', so
        # one needs to be put back on if there was one.
        if path[-1] == posixpath.sep:
            spath = spath + posixpath.sep

        # Remove the leading '/' if it is an absolute path.
        if spath[0] == posixpath.sep:
            spath = spath[1:]

        # Find the position of the first separator.
        index = spath.find(posixpath.sep)

        # The case of no separator, a trailing separator, and a
        # separator in the middle all need to be handled separately.
        if index == -1:
            # As there was no separator, spath specifies the particular
            # setting that is wanted. If it is not in the node's
            # children, then we must throw an error. If it is an actual
            # setting, the value is returned. If it is a parent, then
            # a list of its children is returned.
            if spath not in node['children']:
                raise KeyError('Couldn''t find '
                               + spath
                               + ' in '
                               + node['path']
                               + '.')
            elif 'value' in node['children'][spath]:
                return node['children'][spath]['value']
            else:
                return list(node['children'][spath]['children'].keys())
        elif index == len(spath) - 1:
            # The separator is at the very end, meaning that the actual
            # node is desired regardless of whether it is a parent or
            # not. If it is not in node's children, an error must be
            # raised.
            if spath[:-1] not in node['children']:
                raise KeyError('Couldn''t find '
                               + spath
                               + ' in '
                               + node['path']
                               + '.')
            else:
                return node['children'][spath[:-1]]
        else:
            # The separator is in the middle, meaning that there is more
            # path after it. So, the part before and the part after need
            # to be obtained. If the part before is not in the node's
            # children, an error must be riased. Otherwise, we need to
            # recurse into that node.
            rootpath = spath[:index]
            subpath = spath[index:]
            if rootpath in node['children']:
                return (self._get_setting_by_path_node(
                        node['children'][rootpath],
                        subpath))
            else:
                raise KeyError('Couldn''t find '
                               + rootpath
                               + ' in '
                               + node['path']
                               + '.')

    def _extract_values_node(self, node):
        """ Returns a node stripped down to just its values.

        Parameters
        ----------
        node : dict of settings nodes
            `dict` of settings nodes. Must be a parent, but can contain
            parent and children nodes.

        Returns
        -------
        dict
            A ``dict`` with an element for each node in `node`.
            Parent nodes get turned into a ``dict`` with all their
            children nodes as elements. Setting nodes get reduced to
            being just their value (``name: value``).

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        """
        # Construct the stripped down dictionary of values from this
        # node by going through all its children one by one and
        # extracting values.

        vals = {}

        for k, v in node['children'].items():
            # If it is a parent node, then recurse one level deeper. If
            # it is instead a value node, extract the value.
            if 'children' in v:
                vals[k] = self._extract_values_node(v)
            else:
                vals[k] = v['value']

        return vals

    def _set_values_node(self, node, values, force=False):
        """ Apply a set of values to a settings node.

        Parameters
        ----------
        node : dict of settings nodes
            `dict` of settings nodes. Must be a parent, but can contain
            parent and children nodes.
        values : dict
            A ``dict`` holding the setting value for each node in
            ``tree``. For a setting node, the element in `values` is
            just ``key: value``. For parent nodes in ``tree``, the
            element is a ``dict`` of all the children, which are then
            formatted the same way. Basically, this is the same format
            as the output of :py:meth:`extract_values`
        force : bool, optional
            Whether to write the values to ``tree`` or not if the
            resulting ``tree`` would be made invalid. The default is
            ``False``. Basically, it bypasses the validator.

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        """
        # Iterate through all the children to set everything in the
        # node.

        for k, sv in node['children'].items():

            # Skip if the child node isn't in values.

            if k not in values:
                continue

            # If it is a parent node, then recurse one level deeper. If
            # it is a value node, the value needs to be extracted,
            # possibly converted from its numpy type, and then passed
            # through the validator before being put into tree.

            if 'children' in sv:
                if isinstance(values[k], dict):
                    sv = self._set_values_node(sv, \
                        values[k], force=force)
            else:
                val = values[k]

                # If force=True, we just apply the value. Otherwise, run
                # the validator on the new value and set it if it is
                # valid.

                if force or sv['validator'](val, self._tree, sv):
                    sv['value'] = val

        return node

    def _find_invalids_node(self, node_or_path):
        """ Returns the paths of the invalid nodes in a node.

        Goes through each subnode of `node` and checks whether it is
        valid or not. A list of the paths to the invalid ones is
        returned.

        Parameters
        ----------
        node_or_path : dict of settings nodes or str path
            Either a setting node (``dict`` and must be a parent, but
            can contain parent and children nodes) or a POSIX style path
            ``str`` with ``'/'`` being the root of the settings tree.

        Returns
        -------
        list of str paths
            The list of all the settings that are invalid, as POSIX
            paths.

        Raises
        ------
        KeyError
            If the setting pointed to a path in `path_or_path` cannot be
            found.

        Notes
        -----
        As this function uses recursion to go through all parent nodes,
        they should not be nested too deep or the stack will be
        exhausted.

        """
        # Get the node.
        if isinstance(node_or_path, dict):
            node = node_or_path
        else:
            if node_or_path[-1] == posixpath.sep:
                path = node_or_path
            else:
                path = node_or_path + posixpath.sep
            node = self.get_setting_by_path(path)

        # The course of action depends on whether it is a parent or a
        # setting value node.
        if 'children' in node:
            # If  'children' is not a dict; then the node is invalid.
            if not isinstance(node['children'], dict):
                return [node['path']]

            # Recurse through all of its children, collecting a list of
            # the invalid ones.
            invalids = []
            for k, v in node['children'].items():
                if not isinstance(v, dict) or 'path' not in v:
                    invalids.append(posixpath.join(node['path'] + k))
                else:
                    invalids.extend(self._find_invalids_node(v))
            return invalids
        else:
            # It is a setting value. It must have keys 'value' and
            # 'validator' but not 'children'.

            if 'value' not in node or 'validator' not in node \
                    or 'children' in node:
                return [node['path']]

            # Run the value through the validator, and return if path if
            # invalid or if an exceptiong occurs.
            try:
                if not node['validator'](node['value'], self._tree,
                                         node):
                    return [node['path']]
            except:
                return [node['path']]
            return []

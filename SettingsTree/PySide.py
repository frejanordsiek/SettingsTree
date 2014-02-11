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

""" Module for a PySide control to interact with a settings tree.
"""

import copy
import posixpath

from PySide import QtCore, QtGui
from SettingsTree import SettingsIO


class QSettingsEditor(QtGui.QWidget):
    """ PySide control for editting a tree of settings.

    A PySide control for managing a tree of settings, making them
    editable by a user. This is done by giving using the appropriate
    control for each individual settings and placing them inside
    containers representing their parent settings. All user changes are
    validated before being applied unless the override is set (checkbox
    at the top is unset). Invalid ones are not applied and the
    control for that setting is restored to the current valid value (it
    is assumed that the settings are all initially valid). If a change
    is made which is valid, the signal ``settingsChanged`` is
    emitted. The tree of settings is given as 'settings' and can be
    accessed by the attribute ``settings``.

    Parameters
    ----------
    settings : settings dict
        ``dict`` representing the various settings to be managed. The
        format is discussed in the notes.

    Attributes
    ----------
    settings : dict
    settingsChanged : QtCore.Signal

    See Also
    --------
    SettingsIO
    SettingsIO.settings

    Notes
    -----
    Most of the format is described in ``SettingsIO``. This control does
    use a couple additional fields. Each node (whether it is a parent or
    a node) must have a field 'name' which gives the text to display for
    that setting or parent of settings. Each node also needs a field
    'order' to contain some type that allows all of the nodes in a given
    parent to be sorted (sets display order). For a particular editable
    setting (child), an optional field 'allowed_values', which must be a
    ``list`` of ``str``, gives the only allowed values for that
    setting. All nodes can have an optional 'tooltip' field to supply a
    GUI tooltip for that particular setting.

    """

    #: Signal emitted when the settings have been changed.
    settingsChanged = QtCore.Signal()
    """ Signal emitted when settings has been changed and is valid.

    Whenever the settings are changed and the resulting settings are all
    valid, the signal is emitted. Changes resulting in invalid changes
    do not emit this signal.

    """

    def __init__(self, settings):
        QtGui.QWidget.__init__(self)

        # Create the widget. It is going to be a checkbox for whether
        # to validate all changes and then a QToolBox widget with a
        # page for every parent node. And at a non-parent node, it will
        # be a QtFormLayout. First, we need some layout to put in this
        # widget and then the checkbox and toolbox is put inside of that.

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        self._validation_checkbox = QtGui.QCheckBox('Validate Changes')
        self._validation_checkbox.setCheckState(QtCore.Qt.Checked)
        vbox.addWidget(self._validation_checkbox)

        self._toolbox = QtGui.QToolBox()
        vbox.addWidget(self._toolbox)

        # Store the settings (deep copy) and then make a SettingsIO for
        # it.

        self._settings = copy.deepcopy(settings)
        self._sio = SettingsIO(self._settings)

        # Get the list of all settings nodes and pack them as keys in a
        # dictionary that will hold controls and other information for
        # them.

        self._all_settings = {x:dict() for x in self._sio.list_all()}

        # Create the controls to do the editting and displaying.

        self._create_display_node(self._settings,
                                  self._toolbox)

        # Find the invalid settings and adjust their text.
        self._mark_invalid_settings()

    def _create_display_node(self, node, toolbox):
        # Determine if all the children are parents.

        all_parents = True

        for k, v in node['children'].items():
            if 'is_parent' not in v:
                all_parents = False

        # If they aren't all parents, then there is a problem and this
        # node really needs to be skipped.

        if not all_parents:
            return

        # Add an item for each child and then construct the widgets for
        # that child. They will be sorted in order of the key 'order'.

        for k, v in sorted(list(node['children'].items()), key=
                           lambda pair: pair[1]['order']):
            # Determine whether all of its children are parents or
            # items.

            all_parents = True
            all_settings = True
            for k2, v2 in v['children'].items():
                if 'is_parent' not in v2:
                    all_parents = False
                else:
                    all_settings = False

            # If one and only one is not true, then we have to skip this
            # one because we can't handle mixed parents and settings
            # yet.

            if all_parents == all_settings:
                continue

            # The way it is made depends on whether all the children are
            # parents or not.

            if all_parents:
                # Make another toolbox to put in this one and then
                # recurse to make it. toolbox and the index of the added
                # one need to be stored in _all_settings.

                tb = QtGui.QToolBox()
                self._all_settings[v['path']] = {'type': 'parent', \
                    'name': v['name'], \
                    'toolbox': toolbox, \
                    'item': toolbox.addItem(tb, v['name'])}
                self._create_display_node(v, tb)
            else:
                # Make a blank widget to add to the toolbox, make a
                # formlayout and set the widget's layout. toolbox and
                # the index of the added item need to be stored in
                # _all_settings.

                w = QtGui.QWidget()
                fl = QtGui.QFormLayout()
                w.setLayout(fl)

                self._all_settings[v['path']] = {'type': 'parent', \
                    'name': v['name'], \
                    'toolbox': toolbox, \
                    'item': toolbox.addItem(w, v['name'])}

                # Now, go through all the child settings, figure out
                # what type of control that should be using to edit
                # them, add the controls, put the necessary stuff in
                # __setting_controls, and setup the signals (all go to
                # _control_stateChanged). They will be done in the order
                # of the 'order' field. The function for handling needs
                # to be stored for later use.

                for k2, child in sorted(list(v['children'].items()), \
                        key=lambda pair: pair[1]['order']):
                    if isinstance(child['value'], bool):
                        # bool types will have a checkbox.

                        control = QtGui.QCheckBox()
                        if child['value']:
                            control.setCheckState(QtCore.Qt.Checked)
                        else:
                            control.setCheckState(QtCore.Qt.Unchecked)
                        control.stateChanged.connect( \
                            self._control_stateChanged)
                    elif isinstance(child['value'], (int, float,
                                    complex, str, bytes)):
                        # If we are given the allowed values, then it
                        # will be a combo box. If we are not, then it
                        # will be a line edit.

                        if 'allowed_values' in child:
                            control = QtGui.QComboBox()
                            control.addItems(child['allowed_values'])
                            control.setCurrentIndex(control.findText(
                                                    child['value']))
                            control.currentIndexChanged.connect( \
                                self._control_stateChanged)
                        else:
                            control = QtGui.QLineEdit()
                            control.setText(str(child['value']))
                            control.editingFinished.connect( \
                                self._control_stateChanged)
                    else:
                        # Unsupported type: skip to next.
                        continue

                    # Store reference the the setting in the control.
                    control.settings_path = child['path']

                    # Add the tooltip if it was provided.

                    if 'tooltip' in child:
                        control.setToolTip(child['tooltip'])

                    # Make a label for the control

                    lbl = QtGui.QLabel(child['name'])

                    # Add the label and control to child as a row to fl.

                    fl.addRow(lbl, control)

                    # Add the name and label to _all_settings.

                    self._all_settings[child['path']] = \
                        {'type': 'child', \
                        'name': child['name'], \
                        'label': lbl}

    def _control_stateChanged(self, *args):
        """ Handles changes to the settings from the controls.

        Handles all signals from the controls for manipulating
        settings. This included reading the new setting value,
        validating the changed settings, restoring the old one if it is
        invalid if validation is required, and emitting the
        ``settingsChanged`` signal if it is valid.

        """
        # The control that triggered the signal needs to be gotten, and
        # then the settings node that it is associated with.

        control = self.sender()
        node = self._sio.get_setting_by_path(control.settings_path
                                             + posixpath.sep)

        # Start with the change being considered invalid, so that if an
        # exception or something occurs while checking the new value, it
        # is considered invalid by default. The current value also needs
        # to be grabbed in case it needs to be set back.

        valid = False
        oldvalue = node['value']

        # All exceptions need to be caught because an exception means
        # the value breaks validity.

        try:
            # The way the new value is obtained depends on the value's
            # data type and the type of control used to set it.

            if isinstance(node['value'], bool):
                # The control is a checkbox which is easy to read.
                newvalue = control.isChecked()
            elif isinstance(node['value'], (int, float, complex, str,
                            bytes)):
                # The control stores a string that must be obtained
                # depending on whether it is a LineEdit or a ComboBox.

                if isinstance(control, QtGui.QLineEdit):
                    txt = control.text()
                elif isinstance(control, QtGui.QComboBox):
                    txt = control.currentText()
                else:
                    raise NotImplementedError( \
                                      'Can''t work with control: ' \
                                      + str(type(control)))

                # Extract the text and convert it to get the
                # newvalue. We use the ability of type to give the data
                # type's class and its constructor to convert the string
                # txt to it.

                newvalue = type(oldvalue)(txt)
            else:
                raise NotImplementedError('Can''t work with type: '
                                          + str(type(node['value'])))

            # Apply the new value to node and then check the validity of
            # the whole _settings. The original value will be copied
            # back to it in the case that it is invalid.

            node['value'] = newvalue
            valid = self._sio.check_values()
        except:
            # It is obviously invalid.
            valid = False

        # If it is valid, the settingsChanged signal needs to be
        # emitted. If it is invalid, the old value must be restored and
        # the control needs to be set back to the old value. The signals
        # need to be temporarily turned off while this is done.

        if valid:
            self.settingsChanged.emit()
        elif self._validation_checkbox.isChecked():
            node['value'] = oldvalue

            if isinstance(control, QtGui.QCheckBox):
                control.stateChanged.disconnect( \
                    self._control_stateChanged)
                if oldvalue:
                    control.setCheckState(QtCore.Qt.Checked)
                else:
                    control.setCheckState(QtCore.Qt.Unchecked)
                control.stateChanged.connect( \
                    self._control_stateChanged)
            elif isinstance(control, QtGui.QComboBox):
                control.currentIndexChanged.disconnect( \
                    self._control_stateChanged)
                control.setCurrentIndex(control.findText(
                                        oldvalue))
                control.currentIndexChanged.connect( \
                    self._control_stateChanged)
            elif isinstance(control, QtGui.QLineEdit):
                control.editingFinished.disconnect( \
                    self._control_stateChanged)
                control.setText(str(oldvalue))
                control.editingFinished.connect( \
                    self._control_stateChanged)

        # Remark the invalid settings.
        self._mark_invalid_settings()

    def _mark_invalid_settings(self):
        """ Changes the text of all invalid settings.
        """
        # Go through each setting node.
        for path, v in self._all_settings.items():
            # Adjust the text based on its validity.
            if v['type'] == 'parent':
                if self._sio.check_values(path):
                    txt = v['name']
                else:
                    txt = '!!! ' + v['name'] + ' !!!'
                v['toolbox'].setItemText(v['item'], txt)
            else:
                if self._sio.check_values(path):
                    txt = v['name']
                else:
                    txt = '<b><font color=#FF0000>' \
                          + v['name'] \
                          + '</font></b>'
                v['label'].setText(txt)

    @property
    def settings(self):
        """ Representation of the different settings.

        `settings` is a ``dict`` representing the various settings to be
        managed. The format is described in ``SettingsIO`` other than a
        couple additional fields are used.

        See Also
        --------
        SettingsIO.settings

        """
        return copy.deepcopy(self._settings)

    @property
    def all_valid(self):
        """ Whether all settings are valid or not.

        bool

        """
        return self._sio.check_values()

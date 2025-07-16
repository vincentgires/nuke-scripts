import os
from functools import partial
import nuke
from qtbinding import QtWidgets, QtCore, QtGui

CM_TAB_NAME = 'Connection Manager'
CM_NODES_KNOB = 'connection_manager_nodes'


def get_knob():
    root_node = nuke.root()
    if not root_node.knob(CM_TAB_NAME):
        tab_knob = nuke.Tab_Knob(CM_TAB_NAME)
        root_node.addKnob(tab_knob)
    data_knob = root_node.knob(CM_NODES_KNOB)
    if not data_knob:
        data_knob = nuke.String_Knob(CM_NODES_KNOB, 'Nodes', '')
        root_node.addKnob(data_knob)
    return data_knob


def get_knob_value():
    knob = get_knob()
    if knob is None:
        return
    value = knob.value()
    if value:
        value = value.replace(' ', '').split(',')
    else:
        value = []
    return value


def set_knob_value(value):
    knob = get_knob()
    if knob is not None:
        knob.setValue(value)


def add_node(node_name):
    value = get_knob_value()
    if node_name not in value:
        value.append(node_name)
    set_knob_value(', '.join(value))


def clear_node(node_name):
    value = get_knob_value()
    if node_name in value:
        value.remove(node_name)
    set_knob_value(', '.join(value))


def add_selected_nodes():
    selected_nodes = nuke.selectedNodes()
    for sn in selected_nodes:
        add_node(sn.name())


def connect_input(node_name, node_input=0, optional_input=False):
    selected_nodes = nuke.selectedNodes()
    node = nuke.toNode(node_name)
    for sn in selected_nodes:
        if optional_input:
            node_input = sn.optionalInput()
        sn.setInput(node_input, node)


def display_node(node_name):
    node = nuke.toNode(node_name)
    nuke.connectViewer(0, node)


def select_node(node_name):
    for n in nuke.allNodes():
        n['selected'].setValue(False)
        if n.name() == node_name:
            n['selected'].setValue(True)


def show_node_property(node_name):
    nuke.show(nuke.toNode(node_name))


class ConnectionManagerToolbar(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        super(ConnectionManagerToolbar, self).__init__()
        self.setOrientation(QtCore.Qt.Vertical)

        self.refresh_action = QtWidgets.QAction(
            QtGui.QIcon(os.path.expandvars('$ICONS_PATH/refresh.svg')),
            'Reload', self)
        self.add_action = QtWidgets.QAction(
            QtGui.QIcon(os.path.expandvars('$ICONS_PATH/add.svg')),
            'Add', self)
        self.remove_action = QtWidgets.QAction(
            QtGui.QIcon(os.path.expandvars('$ICONS_PATH/remove.svg')),
            'Remove', self)

        self.connect_input1_action = QtWidgets.QAction('C1', self)
        self.connect_input2_action = QtWidgets.QAction('C2', self)
        self.connect_mask_action = QtWidgets.QAction('CM', self)
        self.view_action = QtWidgets.QAction('View', self)

        self.addAction(self.refresh_action)
        self.addAction(self.add_action)
        self.addAction(self.remove_action)
        self.addSeparator()
        self.addAction(self.connect_input1_action)
        self.addAction(self.connect_input2_action)
        self.addAction(self.connect_mask_action)
        self.addAction(self.view_action)


class ConnectionManagerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ConnectionManagerWidget, self).__init__()
        self.items = QtWidgets.QListWidget()
        self.toolbar = ConnectionManagerToolbar()
        mainlayout = QtWidgets.QHBoxLayout(self)
        mainlayout.addWidget(self.toolbar)
        mainlayout.addWidget(self.items)
        self.setLayout(mainlayout)
        self.installEventFilter(self)
        self.toolbar.refresh_action.triggered.connect(self.update_items)
        self.toolbar.add_action.triggered.connect(self.add_nodes)
        self.toolbar.remove_action.triggered.connect(self.remove_selection)
        self.toolbar.connect_input1_action.triggered.connect(
            partial(self.connect_node, node_input=0))
        self.toolbar.connect_input2_action.triggered.connect(
            partial(self.connect_node, node_input=1))
        self.toolbar.connect_mask_action.triggered.connect(
            partial(self.connect_node, mask_input=True))
        self.toolbar.view_action.triggered.connect(self.view_node)
        self.items.itemDoubleClicked.connect(self.select_item)
        nuke.addOnScriptLoad(self.update_items)

    def add_item(self, text):
        if not self.items.findItems(text, QtCore.Qt.MatchExactly):
            self.items.addItem(text)

    def remove_selection(self):
        for item in self.items.selectedItems():
            index = self.items.indexFromItem(item)
            self.items.takeItem(index.row())
            clear_node(item.text())

    def update_items(self):
        self.items.clear()
        for node_name in get_knob_value():
            self.add_item(node_name)

    def add_nodes(self):
        add_selected_nodes()
        for n in nuke.selectedNodes():
            self.add_item(n.name())

    def select_item(self, item):
        select_node(item.text())
        show_node_property(item.text())

    def view_node(self):
        current_item = self.items.currentItem()
        display_node(current_item.text())

    def connect_node(self, node_input=0, mask_input=False):
        current_item = self.items.currentItem()
        connect_input(
            current_item.text(),
            node_input=node_input,
            optional_input=mask_input)

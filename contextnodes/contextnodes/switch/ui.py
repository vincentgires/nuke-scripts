import nuke
from qtbinding import QtWidgets, QtGui, QtCore, shiboken
from contextnodes.switch import (
    CONTEXT_SWITCH_RULES,
    get_rules,
    update_rules,
    update_context_switch_group_content)


class SwitchContextRulesWidget(QtWidgets.QWidget):
    header_labels = {
        'index': 0,
        'value': 1}
    item_changed = QtCore.Signal(int, object)
    table_updated = QtCore.Signal()
    set_context_clicked = QtCore.Signal()
    clear_context_clicked = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.toolbar = QtWidgets.QToolBar(self)
        self.toolbar.setOrientation(QtCore.Qt.Vertical)
        self.add_button = QtGui.QAction('➕', self)
        self.remove_button = QtGui.QAction('➖', self)
        self.toolbar.addAction(self.add_button)
        self.toolbar.addAction(self.remove_button)
        self.add_button.triggered.connect(self.on_add_button_triggered)
        self.remove_button.triggered.connect(self.on_remove_button_triggered)

        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(len(self.header_labels))
        self.table.setHorizontalHeaderLabels(list(self.header_labels.keys()))
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            self.header_labels['index'],
            QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            self.header_labels['value'],
            QtWidgets.QHeaderView.Stretch)

        layout = QtWidgets.QHBoxLayout(self)
        sublayout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addLayout(sublayout)
        sublayout.addWidget(self.table)

        self.table.itemChanged.connect(self.on_item_changed)

    def on_add_button_triggered(self, _checked: bool = False):
        self.add_item()

    def on_remove_button_triggered(self, _checked: bool = False):
        self.remove_selected()

    def add_item(
            self,
            index: int | None = None,
            value: str | None = None):
        if not shiboken.isValid(self.table):
            return

        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        if index is None:
            index = self.table.rowCount() - 1
        index_item = QtWidgets.QTableWidgetItem(str(index))
        value_item = QtWidgets.QTableWidgetItem(value)

        self.table.setItem(
            row_position, self.header_labels['index'], index_item)
        self.table.setItem(
            row_position, self.header_labels['value'], value_item)

        # Update table row labels with at least one character for easy
        # selection
        for row in range(self.table.rowCount()):
            self.table.setVerticalHeaderItem(
                row, QtWidgets.QTableWidgetItem(''))

    def on_item_changed(self, item):
        row = item.row()
        self.item_changed.emit(row, item)

    def on_checkbox_changed(self, row, state):
        self.item_changed.emit(row, state)

    def on_combobox_changed(self, row, index):
        self.item_changed.emit(row, index)

    def remove_selected(self):
        selection_model = self.table.selectionModel()
        selected_rows = set(
            index.row() for index in selection_model.selectedRows())
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)
        self.table_updated.emit()

    def get_rules(self) -> list[dict]:
        table = self.table
        if not shiboken.isValid(table):
            return
        rules = []
        for row in range(table.rowCount()):
            index_item = table.item(row, self.header_labels['index'])
            value_item = table.item(row, self.header_labels['value'])
            data = {}
            if index_item:
                data['index'] = int(index_item.text())
            if value_item:
                data['value'] = value_item.text()
            if not data:
                continue
            if all(data.get(k) is not None for k in ('index', 'value')):
                rules.append(data)
        return rules


class GroupSwitchContextRulesWidget(QtWidgets.QWidget):
    header_labels = {'value': 0}
    item_changed = QtCore.Signal(int, object)
    table_updated = QtCore.Signal()
    set_context_clicked = QtCore.Signal()
    clear_context_clicked = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.toolbar = QtWidgets.QToolBar(self)
        self.toolbar.setOrientation(QtCore.Qt.Vertical)
        self.add_button = QtGui.QAction('➕', self)
        self.remove_button = QtGui.QAction('➖', self)
        self.toolbar.addAction(self.add_button)
        self.toolbar.addAction(self.remove_button)
        self.add_button.triggered.connect(self.on_add_button_triggered)
        self.remove_button.triggered.connect(self.on_remove_button_triggered)

        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(len(self.header_labels))
        self.table.setHorizontalHeaderLabels(list(self.header_labels.keys()))
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            self.header_labels['value'],
            QtWidgets.QHeaderView.Stretch)

        layout = QtWidgets.QHBoxLayout(self)
        sublayout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addLayout(sublayout)
        sublayout.addWidget(self.table)

        self.table.itemChanged.connect(self.on_item_changed)

    def on_add_button_triggered(self, _checked: bool = False):
        self.add_item()

    def on_remove_button_triggered(self, _checked: bool = False):
        self.remove_selected()

    def add_item(self, value: str | None = None):
        if not shiboken.isValid(self.table):
            return

        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        if value is None:
            value = str(self.table.rowCount() - 1)
        value_item = QtWidgets.QTableWidgetItem(value)

        self.table.setItem(
            row_position, self.header_labels['value'], value_item)

        # Update table row labels with at least one character for easy
        # selection
        for row in range(self.table.rowCount()):
            self.table.setVerticalHeaderItem(
                row, QtWidgets.QTableWidgetItem(''))

    def on_item_changed(self, item):
        row = item.row()
        self.item_changed.emit(row, item)

    def on_checkbox_changed(self, row, state):
        self.item_changed.emit(row, state)

    def on_combobox_changed(self, row, index):
        self.item_changed.emit(row, index)

    def remove_selected(self):
        selection_model = self.table.selectionModel()
        selected_rows = set(
            index.row() for index in selection_model.selectedRows())
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)
        self.table_updated.emit()

    def get_rules(self) -> list[dict]:
        table = self.table
        if not shiboken.isValid(table):
            return
        rules = []
        for row in range(table.rowCount()):
            value_item = table.item(row, self.header_labels['value'])
            data = {}
            if value_item:
                data['value'] = value_item.text()
            if not data:
                continue
            if all(data.get(k) is not None for k in ('value',)):
                rules.append(data)
        return rules


class KnobSwitchRulesWidget(QtWidgets.QWidget):
    def __init__(self, node):
        self.node = node
        self.knob = node[CONTEXT_SWITCH_RULES]
        self.widget = None

    def makeUI(self):  # noqa: N802
        self.widget = SwitchContextRulesWidget()
        self.add_rules()  # Before signals the first time

        self.widget.item_changed.connect(self.update_rules)
        self.widget.table_updated.connect(self.update_rules)

        return self.widget

    def add_rules(self):
        rules = get_rules(node=self.node)
        if rules is None:
            return
        for rule in rules:
            self.widget.add_item(
                index=rule.get('index'),
                value=rule.get('value'))

    def update_rules(self):
        rules = self.widget.get_rules()
        if rules is not None:
            update_rules(self.node, data=rules)


class KnobGroupSwitchRulesWidget(QtWidgets.QWidget):
    def __init__(self, node):
        self.node = node
        self.knob = node[CONTEXT_SWITCH_RULES]
        self.widget = None

    def makeUI(self):  # noqa: N802
        self.widget = GroupSwitchContextRulesWidget()
        self.add_rules()  # Before signals the first time

        self.widget.item_changed.connect(self.update_rules)
        self.widget.table_updated.connect(self.update_rules)

        return self.widget

    def add_rules(self):
        rules = get_rules(node=self.node)
        if rules is None:
            return
        for rule in rules:
            self.widget.add_item(value=rule.get('value'))

    def update_rules(self):
        rules = self.widget.get_rules()
        if rules is not None:
            update_rules(self.node, data=rules)
        update_context_switch_group_content(node=self.node)


def create_rules_knob_widget():
    return KnobSwitchRulesWidget(nuke.thisNode())


def create_group_rules_knob_widget():
    return KnobGroupSwitchRulesWidget(nuke.thisNode())

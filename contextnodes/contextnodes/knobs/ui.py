import nuke
from qtbinding import QtWidgets, QtCore, QtGui, shiboken
from contextnodes.knobs import CONTEXT_RULES
from contextnodes.rules import get_rules, update_rules, build_rule_data
from contextnodes.nodes import set_context_node, clear_context_node


class RulesWidget(QtWidgets.QWidget):
    header_labels = {
        'use': 0,
        'variable': 1,
        'value': 2,
        'mode': 3}
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
        self.add_button.triggered.connect(self.add_item)
        self.remove_button.triggered.connect(self.remove_selected)
        self.set_context_button = QtWidgets.QPushButton('set current')
        self.set_context_button.clicked.connect(self.on_set_context_clicked)
        self.clear_context_button = QtWidgets.QPushButton('remove current')
        self.clear_context_button.clicked.connect(
            self.on_clear_context_clicked)

        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(len(self.header_labels))
        self.table.setHorizontalHeaderLabels(list(self.header_labels.keys()))
        header = self.table.horizontalHeader()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            self.header_labels['use'],
            QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            self.header_labels['variable'],
            QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            self.header_labels['value'],
            QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(
            self.header_labels['mode'],
            QtWidgets.QHeaderView.ResizeToContents)

        layout = QtWidgets.QHBoxLayout(self)
        sublayout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addLayout(sublayout)
        sublayout.addWidget(self.table)
        edit_context_layout = QtWidgets.QHBoxLayout()
        edit_context_layout.addWidget(self.set_context_button)
        edit_context_layout.addWidget(self.clear_context_button)
        sublayout.addLayout(edit_context_layout)

        self.table.itemChanged.connect(self.on_item_changed)

    def add_item(
            self,
            use: bool = True,
            variable: str | None = None,
            value: str | None = None,
            mode: str = 'include'):
        if not shiboken.isValid(self.table):
            return
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        use_checkbox = QtWidgets.QCheckBox()
        use_checkbox.setChecked(use)
        use_checkbox.stateChanged.connect(
            lambda state: self.on_checkbox_changed(row_position, state))
        variable_item = QtWidgets.QTableWidgetItem(variable)
        value_item = QtWidgets.QTableWidgetItem(value)
        mode_combobox = QtWidgets.QComboBox()
        mode_combobox.addItems(['include', 'exclude'])
        mode_combobox.setCurrentText(mode)
        mode_combobox.currentIndexChanged.connect(
            lambda index: self.on_combobox_changed(row_position, index))

        self.table.setCellWidget(
            row_position, self.header_labels['use'], use_checkbox)
        self.table.setItem(
            row_position, self.header_labels['variable'], variable_item)
        self.table.setItem(
            row_position, self.header_labels['value'], value_item)
        self.table.setCellWidget(
            row_position, self.header_labels['mode'], mode_combobox)

    def on_item_changed(self, item):
        row = item.row()
        self.item_changed.emit(row, item)

    def on_checkbox_changed(self, row, state):
        self.item_changed.emit(row, state)

    def on_combobox_changed(self, row, index):
        self.item_changed.emit(row, index)

    def on_set_context_clicked(self):
        self.set_context_clicked.emit()

    def on_clear_context_clicked(self):
        self.clear_context_clicked.emit()

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
            use_widget = table.cellWidget(row, self.header_labels['use'])
            variable_item = table.item(row, self.header_labels['variable'])
            value_item = table.item(row, self.header_labels['value'])
            mode_widget = table.cellWidget(row, self.header_labels['mode'])
            build_arguments = {}
            if use_widget:
                build_arguments['use'] = use_widget.isChecked()
            if variable_item:
                build_arguments['variable'] = variable_item.text()
            if value_item:
                build_arguments['value'] = value_item.text()
            if mode_widget:
                build_arguments['mode'] = mode_widget.currentText()
            if not build_arguments:
                continue
            if all(build_arguments.get(k) for k in ('variable', 'value')):
                rule = build_rule_data(**build_arguments)
                rules.append(rule)
        return rules


class KnobRulesWidget(QtWidgets.QWidget):
    def __init__(self, node):
        self.node = node
        self.knob = node[CONTEXT_RULES]
        self.widget = None

    def makeUI(self):  # noqa: N802
        self.widget = RulesWidget()
        self.add_rules()  # Before signals the first time

        self.widget.item_changed.connect(self.update_rules)
        self.widget.table_updated.connect(self.update_rules)
        self.widget.set_context_clicked.connect(self.set_context)
        self.widget.clear_context_clicked.connect(self.clear_context)

        return self.widget

    def add_rules(self):
        rules = get_rules(node=self.node)
        if rules is None:
            return
        for rule in rules:
            context_variable, context_value = rule['context']
            self.widget.add_item(
                use=rule['use'],
                variable=context_variable,
                value=context_value,
                mode=rule['mode'])

    def update_rules(self):
        rules = self.widget.get_rules()
        if rules is not None:
            update_rules(self.node, data=rules)

    def set_context(self):
        set_context_node(self.node)

    def clear_context(self):
        clear_context_node(self.node)


def create_rules_knob_widget():
    return KnobRulesWidget(nuke.thisNode())

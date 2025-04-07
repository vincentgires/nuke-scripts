import nuke
from PySide2 import QtWidgets, QtCore
from contextnodes.knobs import CONTEXT_RULES
from contextnodes.rules import get_rules, update_rules, build_rule_data


class RulesWidget(QtWidgets.QWidget):
    header_labels = {
        'use': 0,
        'variable': 1,
        'value': 2,
        'mode': 3}
    item_changed = QtCore.Signal(int, object)
    table_updated = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.toolbar = QtWidgets.QToolBar(self)
        self.toolbar.setOrientation(QtCore.Qt.Vertical)
        self.add_button = QtWidgets.QAction('➕', self)
        self.remove_button = QtWidgets.QAction('➖', self)
        self.toolbar.addAction(self.add_button)
        self.toolbar.addAction(self.remove_button)
        self.add_button.triggered.connect(self.add_item)
        self.remove_button.triggered.connect(self.remove_selected)

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
        layout.addWidget(self.toolbar)
        layout.addWidget(self.table)

        self.table.itemChanged.connect(self.on_item_changed)

    def add_item(
            self,
            use: bool = True,
            variable: str | None = None,
            value: str | None = None,
            mode: str = 'include'):
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

    def remove_selected(self):
        selection_model = self.table.selectionModel()
        selected_rows = set(
            index.row() for index in selection_model.selectedRows())
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)
        self.table_updated.emit()

    def get_rules(self) -> list[dict]:
        rules = []
        table = self.table
        for row in range(table.rowCount()):
            use_widget = table.cellWidget(row, self.header_labels['use'])
            use = use_widget.isChecked() if use_widget else None
            variable_item = table.item(row, self.header_labels['variable'])
            variable = variable_item.text() if variable_item else None
            value_item = table.item(row, self.header_labels['value'])
            value = value_item.text() if value_item else None
            mode_widget = table.cellWidget(row, self.header_labels['mode'])
            mode = mode_widget.currentText() if mode_widget else None
            rule = build_rule_data(
                variable=variable,
                value=value,
                use=use,
                mode=mode)
            if variable and value:
                rules.append(rule)
        return rules


class KnobRulesWidget(QtWidgets.QWidget):
    def __init__(self, node):
        self.node = node
        self.knob = node[CONTEXT_RULES]
        self.widget = None

    def makeUI(self):  # noqa: N802
        self.widget = RulesWidget()
        rules = get_rules(node=self.node)
        if rules:
            for rule in rules:
                context_variable, context_value = rule['context']
                self.widget.add_item(
                    use=rule['use'],
                    variable=context_variable,
                    value=context_value,
                    mode=rule['mode'])

        self.widget.item_changed.connect(self.update_rules)
        self.widget.table_updated.connect(self.update_rules)

        return self.widget

    def update_rules(self):
        update_rules(self.node, data=self.widget.get_rules())


def create_rules_knob_widget():
    return KnobRulesWidget(nuke.thisNode())

import json
from contextlib import contextmanager
import nuke
import nukescripts.create
from qtbinding import QtCore
from vgnuke.knobs import create_knob
from vgnuke.root import is_root_available
from contextnodes.knobs import CONTEXT_TAB
from contextnodes.nodes import (
    get_default_graph_scope_variables, match_rule_value)

CONTEXT_SWITCH_VARIABLE = 'contextswitch_variable'
CONTEXT_SWITCH_RULES = 'contextswitch_rules'
CONTEXT_SWITCH_RULES_PY = 'contextswitch_rules_py'
NODE_NAME = 'ContextSwitch'


@contextmanager
def enter_group(group):
    group.begin()
    yield group
    group.end()


def sync_variable_knob():
    node = nuke.thisNode()
    if CONTEXT_SWITCH_VARIABLE not in node.knobs():
        return
    value = node[CONTEXT_SWITCH_VARIABLE].value()
    with enter_group(node) as _:
        if switch_node := nuke.toNode('Switch'):
            switch_node[CONTEXT_SWITCH_VARIABLE].setValue(value)


def add_custom_switch_knob(
        node: nuke.Node = None,
        on_create: bool = False,
        group: bool = False):
    node = node or nuke.thisNode()
    rules_knob = node.knob(CONTEXT_SWITCH_RULES)
    if not rules_knob:
        return
    rules_knob.setFlag(nuke.INVISIBLE)

    knob_py = (
        'create_group_rules_knob_widget'
        if group else 'create_rules_knob_widget')

    def set_value(py_knob):
        # Custom UI knob
        py_knob.setValue(
            "__import__('importlib').import_module('contextnodes.switch.ui')"
            f".{knob_py}()")
        if node.Class() != 'Switch':
            return
        # which knob
        expression = (
            "[python -execlocal ret="
            "__import__('importlib').import_module('contextnodes.switch')"
            ".resolve_index(node=nuke.thisNode())]")
        which_knob = node['which']
        which_knob.setExpression(expression)
        which_knob.setFlag(nuke.INVISIBLE)
        if mode_knob := node.knob('mode'):  # For Nuke 15, it no longer exists
            # in Nuke 16.
            mode_knob.setFlag(nuke.INVISIBLE)

    if py_knob := node.knob(CONTEXT_SWITCH_RULES_PY):
        if on_create:
            # Set knob value from addOnCreate callback
            QtCore.QTimer.singleShot(0, lambda: set_value(py_knob))
        else:
            set_value(py_knob)
    else:
        py_knob = nuke.PyCustom_Knob(CONTEXT_SWITCH_RULES_PY, 'rules')
        py_knob.setFlag(nuke.STARTLINE)
        set_value(py_knob)
        node.addKnob(py_knob)


def create_context_switch_node(
        group: bool = False, name: str | None = None, local: bool = True):
    node_class = 'Group' if group else 'Switch'
    if local:
        node = nukescripts.create.createNodeLocal(node_class, inpanel=False)
    else:
        node = nuke.createNode(node_class, inpanel=False)
    node.setName(name or NODE_NAME)
    if not node.knob(CONTEXT_TAB):
        tab_knob = nuke.Tab_Knob(CONTEXT_TAB, NODE_NAME, False)
        node.addKnob(tab_knob)
    # Custom knobs
    create_knob(node, 'STRING', CONTEXT_SWITCH_VARIABLE, 'variable', '')
    create_knob(node, 'STRING', CONTEXT_SWITCH_RULES, 'rules', '')
    add_custom_switch_knob(node, group=group)
    if node_class == 'Group':
        nuke.addKnobChanged(sync_variable_knob, node=node)
    return node


def get_rules(node: nuke.Node) -> list[dict] | None:
    if CONTEXT_SWITCH_RULES not in node.knobs():
        return
    if rules := node[CONTEXT_SWITCH_RULES].value():
        rules = json.loads(rules)
        return rules


def update_rules(node: nuke.Node, data: list[dict]):
    node[CONTEXT_SWITCH_RULES].setValue(json.dumps(data))


def resolve_index(node: nuke.Node):
    if not is_root_available():  # HACK: check root availibilty to avoid issue
        # on loading .nk file.
        return
    variable = node[CONTEXT_SWITCH_VARIABLE].value()
    if not variable:
        return
    rules = get_rules(node)
    if rules is None:
        return
    test_value = get_default_graph_scope_variables().get(variable)
    for rule in reversed(rules):
        rule_value = rule.get('value')
        index = rule.get('index')
        if match_rule_value(test_value=test_value, rule_value=rule_value):
            return index
    return 0


def update_context_switch_group_content(node: nuke.Node | None = None):
    node = node or nuke.thisNode()
    rules = get_rules(node)

    def get_input_nodes():
        nodes = [n for n in group.nodes() if n.Class() == 'Input']
        return sorted(nodes, key=lambda n: n['number'].value())

    with enter_group(node) as group:
        # Get all inputs
        input_nodes = get_input_nodes()

        # Clean unassigned from rules
        for n in input_nodes[len(rules):]:
            nuke.delete(n)

        # Refresh inputs
        input_nodes = get_input_nodes()

        # Sync (match rules and inputs)
        for i, rule in enumerate(rules):
            if i >= len(input_nodes):
                input_nodes.append(nuke.nodes.Input())
            input_nodes[i].setName(f"Input{rule['value']}")

        # Context control
        switch_node = nuke.toNode('Switch')
        if switch_node is None:
            switch_node = create_context_switch_node(
                group=False, name='Switch', local=False)
        switch_rules = [
            {'index': i, 'value': rule['value']}
            for i, rule in enumerate(rules)]
        update_rules(node=switch_node, data=switch_rules)

        # Create or get output
        ouput_node = nuke.toNode('Output1')
        if ouput_node is None:
            ouput_node = nuke.nodes.Output(name='Output1')

        # Connect inputs and output to switch
        for i, input_node in enumerate(input_nodes):
            switch_node.setInput(i, input_node)
        ouput_node.setInput(0, switch_node)


if __name__ == '__main__':
    create_context_switch_node()

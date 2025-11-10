import json
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


def add_custom_switch_knob(node: nuke.Node = None, on_create: bool = False):
    node = node or nuke.thisNode()
    rules_knob = node.knob(CONTEXT_SWITCH_RULES)
    if not rules_knob:
        return
    rules_knob.setFlag(nuke.INVISIBLE)

    def set_value(py_knob):
        # Custom UI knob
        py_knob.setValue(
            "__import__('importlib').import_module('contextnodes.switch.ui')"
            ".create_rules_knob_widget()")
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


def create_context_switch():
    node = nukescripts.create.createNodeLocal('Switch', inpanel=False)
    node.setName(NODE_NAME)
    if not node.knob(CONTEXT_TAB):
        tab_knob = nuke.Tab_Knob(CONTEXT_TAB, NODE_NAME, False)
        node.addKnob(tab_knob)
    if node.Class() == 'Switch':
        # Custom knobs
        create_knob(node, 'STRING', CONTEXT_SWITCH_VARIABLE, 'variable', '')
        create_knob(node, 'STRING', CONTEXT_SWITCH_RULES, 'rules', '')
        add_custom_switch_knob(node)
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


if __name__ == '__main__':
    create_context_switch()

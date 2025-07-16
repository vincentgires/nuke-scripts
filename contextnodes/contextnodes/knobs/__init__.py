import nuke
from qtbinding import QtCore
from vgnuke.knobs import create_knob

CONTEXT_TAB = 'context_tab'
CONTEXT_TAGS_KNOB = 'context_tags'
CONTEXT_RULES = 'context_rules'
CONTEXT_RULES_PY = 'context_rules_py'


def add_custom_rules_knob(node: nuke.Node = None, on_create: bool = False):
    node = node or nuke.thisNode()
    if not node.knob(CONTEXT_RULES):
        return

    def set_value(knob):
        knob.setValue(
            "__import__('importlib').import_module('contextnodes.knobs.ui')"
            ".create_rules_knob_widget()")

    if knob := node.knob(CONTEXT_RULES_PY):
        if on_create:
            # Set knob value from addOnCreate callback
            QtCore.QTimer.singleShot(0, lambda: set_value(knob))
        else:
            set_value(knob)
    else:
        knob = nuke.PyCustom_Knob(CONTEXT_RULES_PY, 'rules')
        knob.setFlag(nuke.STARTLINE)
        set_value(knob)
        node.addKnob(knob)


def add_context_knobs(
        node: nuke.Node = None,
        force: bool = False):
    node = node or nuke.thisNode()
    if not node.knob(CONTEXT_TAB):
        tab_knob = nuke.Tab_Knob(CONTEXT_TAB, 'Context', False)
        node.addKnob(tab_knob)
    if node.Class() == 'BackdropNode' or force:
        rules_knob = create_knob(node, 'STRING', CONTEXT_RULES, 'rules', '')
        rules_knob.setFlag(nuke.INVISIBLE)
        add_custom_rules_knob(node)
    if node.Class() == 'Root':
        create_knob(node, 'STRING', CONTEXT_TAGS_KNOB, 'tags', '')

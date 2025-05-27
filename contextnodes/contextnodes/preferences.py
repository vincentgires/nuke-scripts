import nuke
from vgnuke.knobs import create_knob

PREFS_TAB_NAME = 'contextnodes_preferences'
PREFS_TAB_LABEL = 'Context Nodes'
PREFS_BACKDROP_APPEARANCE_KNOB = 'contextnodes_backdrop_appearance'


def get_preferences_node():
    return nuke.toNode('preferences')


def create_preferences_knobs():
    node = get_preferences_node()

    if not node.knob(PREFS_TAB_NAME):
        knob = nuke.Tab_Knob(PREFS_TAB_NAME, PREFS_TAB_LABEL)
        node.addKnob(knob)

    create_knob(
        node, 'ENUMERATE',
        PREFS_BACKDROP_APPEARANCE_KNOB, 'backdrop appearance',
        ['Border', 'Fill'])

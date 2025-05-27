from functools import partial
import nuke
from contextnodes.knobs import add_custom_rules_knob
from contextnodes.nodes import auto_label, update_content
from contextnodes.preferences import create_preferences_knobs

if nuke.GUI:
    nuke.addOnCreate(
        partial(add_custom_rules_knob, on_create=True),
        nodeClass='BackdropNode')
    nuke.addKnobChanged(update_content, nodeClass='*')
    nuke.addAutolabel(auto_label, nodeClass='BackdropNode')
    # Autolabel is not working on * nodes. For all other node classes than
    # BackdropNode, it is set in update_content() function.

    # Preferences
    nuke.addOnCreate(create_preferences_knobs, nodeClass='Root')
    # Root is used instead of Preferences because it does not seem to
    # support callbacks.

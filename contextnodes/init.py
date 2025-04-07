from functools import partial
import nuke
from contextnodes.knobs import add_custom_rules_knob

if nuke.GUI:
    nuke.addOnCreate(
        partial(add_custom_rules_knob, on_create=True),
        nodeClass='BackdropNode')

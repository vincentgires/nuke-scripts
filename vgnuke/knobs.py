import nuke
from nuke import Knob
from .typing import Node

knob_constructors = {
    'STRING': nuke.String_Knob,
    'ENUMERATE': nuke.Enumeration_Knob,
    'TEXT': nuke.Text_Knob,
    'NUMBER': nuke.Int_Knob,
    'BOOLEAN': nuke.Boolean_Knob,
    'SCRIPT': nuke.Script_Knob,
    'RADIO': nuke.Radio_Knob,
    'COLOR_CHIP': nuke.ColorChip_Knob}


def create_knob(
        node: Node,
        subtype: str,
        name: str,
        label: str = '',
        value: str = '',
        newline: bool = False,
        disable: bool = False) -> Knob:
    knob = node.knob(name)
    if knob is not None:
        return knob
    knob = knob_constructors[subtype](name, label, value)
    node.addKnob(knob)
    if newline:
        knob.setFlag(nuke.STARTLINE)
    if disable:
        knob.setFlag(nuke.DISABLED)
    return knob


def get_knob_value(node: Node, name: str) -> Node:
    if name not in node.knobs():
        return
    return node[name].value()

import nuke


def create_knob(
        node, subtype, name, label='', value='', newline=False, disable=False):
    knob = node.knob(name)
    if knob is not None:
        return knob
    if subtype == 'STRING':
        Knob = nuke.String_Knob  # noqa: N806
    elif subtype == 'ENUMERATE':
        Knob = nuke.Enumeration_Knob  # noqa: N806
    elif subtype == 'TEXT':
        Knob = nuke.Text_Knob  # noqa: N806
    elif subtype == 'NUMBER':
        Knob = nuke.Int_Knob  # noqa: N806
    elif subtype == 'BOOLEAN':
        Knob = nuke.Boolean_Knob  # noqa: N806
    elif subtype == 'SCRIPT':
        Knob = nuke.Script_Knob  # noqa: N806
    elif subtype == 'RADIO':
        Knob = nuke.Radio_Knob  # noqa: N806
    knob = Knob(name, label, value)
    node.addKnob(knob)
    if newline:
        knob.setFlag(nuke.STARTLINE)
    if disable:
        knob.setFlag(nuke.DISABLED)
    return knob


def get_knob_value(node, name):
    if name not in node.knobs():
        return
    return node[name].value()

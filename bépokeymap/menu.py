# coding: utf8

import nuke
import nukescripts
from functools import partial


def invert_disable():
    for n in nuke.selectedNodes():
        knob = n['disable']
        knob.setValue(not knob.value())


menu = nuke.menu('Nuke').addMenu('bépokeymap')
menu.addCommand('Undo', nuke.undo, 'ctrl+à')
menu.addCommand('Redo', nuke.redo, 'ctrl+y')
menu.addCommand('Save', nuke.scriptSave, 'ctrl+u')
menu.addCommand('Select pattern', nuke.selectPattern, 'f3')
menu.addCommand(
    'Connect viewer 1 to selection',
    partial(nukescripts.connect_selected_to_viewer, 0), '"')
menu.addCommand(
    'Connect viewer 2 to selection',
    partial(nukescripts.connect_selected_to_viewer, 1), '«')
menu.addCommand(
    'Connect viewer 3 to selection',
    partial(nukescripts.connect_selected_to_viewer, 2), '»')
menu.addCommand(
    'Connect viewer 4 to selection',
    partial(nukescripts.connect_selected_to_viewer, 3), '(')
menu.addCommand(
    'Connect viewer 5 to selection',
    partial(nukescripts.connect_selected_to_viewer, 4), ')')
menu.addCommand('Autoplace snap all', nuke.autoplace_snap_all, 'é')
menu.addCommand('Invert disable', invert_disable, 'e')

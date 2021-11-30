# coding: utf8

import nuke
import nukescripts
from functools import partial

shortcut_context = {'window': 0, 'application': 1, 'dag': 2}


def invert_disable():
    for n in nuke.selectedNodes():
        knob = n['disable']
        knob.setValue(not knob.value())


def zoom(direction, factor=0.5):
    z = nuke.zoom()
    value = z * factor
    if direction == '+':
        v = z + value
    elif direction == '-':
        v = z - value
    nuke.zoom(v, nuke.center())


menu = nuke.menu('Nuke').addMenu('bépokeymap')
menu.addCommand('Undo', nuke.undo, 'ctrl+à')
menu.addCommand('Redo', nuke.redo, 'ctrl+y')
menu.addCommand('Save', nuke.scriptSave, 'ctrl+u')
menu.addCommand('Select pattern', nuke.selectPattern, 'f3')
menu.addCommand('Zoom +', partial(zoom, '+'), ',')
menu.addCommand('Zoom -', partial(zoom, '-'), 'è')
menu.addCommand(
    'Connect viewer 1 to selection',
    partial(nukescripts.connect_selected_to_viewer, 0), '"',
    shortcutContext=shortcut_context['dag'])
menu.addCommand(
    'Connect viewer 2 to selection',
    partial(nukescripts.connect_selected_to_viewer, 1), '«',
    shortcutContext=shortcut_context['dag'])
menu.addCommand(
    'Connect viewer 3 to selection',
    partial(nukescripts.connect_selected_to_viewer, 2), '»',
    shortcutContext=shortcut_context['dag'])
menu.addCommand(
    'Connect viewer 4 to selection',
    partial(nukescripts.connect_selected_to_viewer, 3), '(',
    shortcutContext=shortcut_context['dag'])
menu.addCommand(
    'Connect viewer 5 to selection',
    partial(nukescripts.connect_selected_to_viewer, 4), ')',
    shortcutContext=shortcut_context['dag'])
menu.addCommand(
    'Autoplace snap all', nuke.autoplace_snap_all, 'é',
    shortcutContext=shortcut_context['dag'])
menu.addCommand(
    'Invert disable', invert_disable, 'e',
    shortcutContext=shortcut_context['dag'])

from contextnodes.nodes import (
    set_context_backdrops_from_selection, set_context_nodes_from_selection)
from contextnodes.switch import create_context_switch_node
import nuke
import nukescripts.create
from functools import partial

MENU_NAME = 'Context'


def create_menus():
    nuke_menu = nuke.menu('Nuke')
    menu = nuke_menu.addMenu(MENU_NAME)
    menu.addCommand(
        name='Set Context Backdrops',
        command=set_context_backdrops_from_selection,
        shortcut='f2')
    menu.addCommand(
        name='Set Current Nodes',
        command=set_context_nodes_from_selection,
        shortcut='alt+f2')
    menu.addCommand(
        name='Create ContextSwitch (Gizmo)',
        command=partial(
            nukescripts.create.createNodeLocal,
            'ContextSwitch',
            inpanel=False))
    menu.addCommand(
        name='Create ContextSwitch (Group)',
        command=partial(create_context_switch_node, group=True))
    menu.addCommand(
        name='Create ContextSwitch (Switch)',
        command=create_context_switch_node)

    nuke_toolbar = nuke.toolbar('Nodes')
    cn_menu = nuke_toolbar.addMenu('ContextNodes')
    cn_menu.addCommand(
        name='ContextSwitch (Gizmo)',
        command=partial(
            nukescripts.create.createNodeLocal,
            'ContextSwitch',
            inpanel=False))
    cn_menu.addCommand(
        name='ContextSwitch (Group)',
        command=partial(create_context_switch_node, group=True))
    cn_menu.addCommand(
        name='ContextSwitch (Switch)',
        command=create_context_switch_node)


create_menus()

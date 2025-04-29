from contextnodes.nodes import (
    set_context_backdrops_from_selection, set_context_nodes_from_selection)
import nuke

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


create_menus()

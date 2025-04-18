from contextnodes.nodes import create_context_backdrops_from_selection
import nuke

MENU_NAME = 'Context'


def create_menus():
    nuke_menu = nuke.menu('Nuke')
    menu = nuke_menu.addMenu(MENU_NAME)
    menu.addCommand(
        name='Create Context Backdrops',
        command=create_context_backdrops_from_selection,
        shortcut='f2')


create_menus()

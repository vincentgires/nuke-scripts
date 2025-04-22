from contextnodes.nodes import set_context_backdrops_from_selection
import nuke

MENU_NAME = 'Context'


def create_menus():
    nuke_menu = nuke.menu('Nuke')
    menu = nuke_menu.addMenu(MENU_NAME)
    menu.addCommand(
        name='Set Context Backdrops',
        command=set_context_backdrops_from_selection,
        shortcut='f2')


create_menus()

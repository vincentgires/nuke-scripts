import nuke
import nukescripts.create
from contextnodes.knobs import add_context_knobs
from vgnuke.nodetree import get_grid_size

CONTEXT_BACKDROP_NAME = 'ContextBackdrop'
FONT_SIZE = 16
ENABLE_COLOR = 1099839487
DISABLE_COLOR = 2385983487
LABEL_COLOR = 4294967295


def get_selected_nodes_by_group() -> dict[nuke.Group, nuke.Node]:
    selected_nodes_by_group = {}

    def check_node(node, parent_group=None):
        if node['selected'].value():
            group = parent_group if parent_group else nuke.root()
            if group not in selected_nodes_by_group:
                selected_nodes_by_group[group] = []
            selected_nodes_by_group[group].append(node)
        if node.Class() == 'Group':
            for internal_node in node.nodes():
                check_node(internal_node, parent_group=node)

    for node in nuke.allNodes():
        check_node(node)

    return selected_nodes_by_group


def create_backdrops_for_selected_node() -> list[nuke.BackdropNode]:
    selected_nodes_by_group = get_selected_nodes_by_group()
    backdrops = []

    for group, nodes in selected_nodes_by_group.items():
        if not nodes:
            continue

        with group:  # Allow to create backdrops under each groups
            backdrop = nukescripts.create.createNodeLocal(
                'BackdropNode', inpanel=False)
            backdrops.append(backdrop)

            # Define size from nodes
            minx, miny, maxx, maxy = (
                float('inf'), float('inf'), float('-inf'), float('-inf'))
            for node in nodes:
                x, y = node['xpos'].value(), node['ypos'].value()
                x = x + node.screenWidth() / 2
                y = y + node.screenHeight() / 2
                if x < minx:
                    minx = x
                if y < miny:
                    miny = y
                if x > maxx:
                    maxx = x
                if y > maxy:
                    maxy = y

            # Adjust size with padding from grid size
            grid_width, grid_height = get_grid_size()
            width = maxx - minx + grid_width * 2
            height = maxy - miny + grid_height * 4

            center_x = (minx + maxx) / 2
            center_y = (miny + maxy) / 2

            # Move backdrop
            backdrop['xpos'].setValue(center_x - width / 2)
            backdrop['ypos'].setValue((center_y - height / 2) - grid_height)
            backdrop['bdwidth'].setValue(width)
            backdrop['bdheight'].setValue(height)

    return backdrops


def create_context_backdrops() -> list[nuke.BackdropNode]:
    backdrops = create_backdrops_for_selected_node()
    for bd in backdrops:
        add_context_knobs(node=bd)
        bd['appearance'].setValue('Border')
        bd.setName(CONTEXT_BACKDROP_NAME)
        bd['note_font_size'].setValue(FONT_SIZE)
        bd['note_font_color'].setValue(LABEL_COLOR)
    return backdrops


if __name__ == '__main__':
    create_context_backdrops()

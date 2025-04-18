import nuke
import nukescripts.create
from PySide2 import QtCore
from contextnodes.knobs import CONTEXT_RULES, add_context_knobs
from contextnodes.rules import build_rule_data, update_rules, get_rules
from vgnuke.nodetree import get_grid_size

CONTEXT_BACKDROP_NAME = 'ContextBackdrop'
FONT_SIZE = 16
ENABLE_COLOR = 1099839487
DISABLE_COLOR = 2385983487
LABEL_COLOR = 4294967295

context_value_separator = ','


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


def _get_graph_scope_variables(node: nuke.Node | None = None):
    node = node or nuke.root()
    gsv_data = node.knobs().get('gsv').value()
    gsv_default_data = gsv_data.get('Default')
    return gsv_default_data


def add_context_from_gsv(
        node: nuke.Node,
        filter_variables: list | None = None,
        merge: bool = True):
    gsv_data = _get_graph_scope_variables()
    for variable, value in gsv_data.items():
        if filter_variables is not None and variable not in filter_variables:
            continue
        append = True
        if merge:
            rules = get_rules(node) or []
            for rule in reversed(rules):
                rule_variable, rule_value = rule['context']
                if rule_variable == variable:
                    append = False
                    rule_values = rule_value.split(context_value_separator)
                    if value in rule_values:
                        break
                    rule_values.append(value)
                    rule_value = context_value_separator.join(
                        sorted(rule_values))
                    rule['context'] = [rule_variable, rule_value]
                    break
            if not append:
                update_rules(node=node, data=rules)
        if append:
            rule_data = build_rule_data(variable=variable, value=value)
            update_rules(node=node, data=rule_data)


def create_context_backdrops() -> list[nuke.BackdropNode]:
    backdrops = create_backdrops_for_selected_node()
    for bd in backdrops:
        add_context_knobs(node=bd)
        bd['appearance'].setValue('Border')
        bd.setName(CONTEXT_BACKDROP_NAME)
        bd['note_font_size'].setValue(FONT_SIZE)
        bd['note_font_color'].setValue(LABEL_COLOR)
    return backdrops


def create_context_backdrops_from_selection():
    nodes = nuke.selectedNodes()
    backdrops = [
        n for n in nodes
        if n.Class() == 'BackdropNode' and n.knob(CONTEXT_RULES)]
    if not backdrops:
        backdrops = create_context_backdrops()
    for node in backdrops:
        node.hideControlPanel()  # Avoid dealing with knob callback and Qt
        # signals
        for fct in add_context_callbacks:
            fct(node)
        QtCore.QTimer.singleShot(0, lambda: node.showControlPanel())


add_context_callbacks = [add_context_from_gsv]

if __name__ == '__main__':
    create_context_backdrops()

import fnmatch
from typing import Callable
import nuke
import nukescripts.create
from contextnodes.knobs import CONTEXT_RULES, add_context_knobs
from contextnodes.rules import build_rule_data, update_rules, get_rules
from contextnodes.preferences import (
    PREFS_BACKDROP_APPEARANCE_KNOB,
    get_preferences_node)
from qtbinding import QtCore
from vgnuke.nodetree import get_grid_size, get_all_instances
from vgnuke.root import is_root_available
from vgnuke.knobs import get_knob_value
from vgnuke.backdrop import get_content as get_backdrop_content

CONTEXT_BACKDROP_NAME = 'ContextBackdrop'
FONT_SIZE = 16
ENABLE_COLOR = 1099839487
DISABLE_COLOR = 2385983487
LABEL_COLOR = 4294967295

context_value_separator = ','


def auto_label(node: nuke.Node | None = None):
    node = node or nuke.thisNode()
    if CONTEXT_RULES not in node.knobs():
        return
    context_rules_knob = node.knob(CONTEXT_RULES)
    if context_rules_knob is None:
        return
    rules = get_rules(node)
    if rules is None:
        return
    label = '' if node.Class() == 'BackdropNode' else node.name()
    for rule in rules:
        if not rule['use']:
            continue
        rule_variable, rule_value = rule['context']
        rule_mode = rule['mode']
        operation = '!=' if rule_mode == 'exclude' else '='
        rule_display = (
            f'{rule_variable} {operation} ' if len(rules) > 1 else '')
        label += f'<center>{rule_display}{rule_value}</center>'
        if rule_mode == 'exclude':
            label += (
                '<center><span style="background-color: dimgray;">'
                '<font size=2 color=gainsboro>exclude</font>'
                '</span></center>')
    label += node['label'].value()
    return label


def auto_label_node(node=None):
    node = node or nuke.thisNode()
    label = auto_label(node)
    return label


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
        process_value: Callable | None = None,
        merge: bool = True):
    gsv_data = _get_graph_scope_variables()
    for variable, value in gsv_data.items():
        if filter_variables is not None and variable not in filter_variables:
            continue
        append = True
        if process_value is not None:
            value = process_value(value)
        if merge:
            rules = get_rules(node) or []
            for rule in reversed(rules):
                rule_variable, rule_value = rule['context']
                if rule_variable == variable:
                    append = False
                    rule_values = rule_value.split(context_value_separator)
                    rule_values = [x.strip() for x in rule_values]
                    if value in rule_values:
                        break
                    rule_values.append(value)
                    rule_value = (context_value_separator + ' ').join(
                        sorted(rule_values))
                    rule['context'] = [rule_variable, rule_value]
                    break
            if not append:
                update_rules(node=node, data=rules)
        if append:
            rule_data = build_rule_data(variable=variable, value=value)
            update_rules(node=node, data=rule_data)


def remove_context_from_gsv(
        node: nuke.Node,
        filter_variables: list | None = None,
        match_value: Callable | None = None):
    gsv_data = _get_graph_scope_variables()
    for variable, value in gsv_data.items():
        if filter_variables is not None and variable not in filter_variables:
            continue
        rules = get_rules(node) or []
        is_updated = False
        for rule in reversed(rules):  # Reversed to allow delete item
            rule_variable, rule_value = rule['context']
            if rule_variable == variable:
                rule_values = rule_value.split(context_value_separator)
                rule_values = [x.strip() for x in rule_values]
                value_to_check = value
                if match_value is not None:
                    value_to_check = match_value(rule_values, value)
                if value_to_check not in rule_values:
                    continue
                is_updated = True
                rule_values.remove(value_to_check)
                if rule_values:
                    rule_value = (context_value_separator + ' ').join(
                        sorted(rule_values))
                    rule['context'] = [rule_variable, rule_value]
                else:
                    rules.remove(rule)
        if is_updated:
            update_rules(node=node, data=rules)


def _set_context_look(node):
    if node.Class() == 'BackdropNode':
        node['note_font_size'].setValue(FONT_SIZE)
    node['note_font_color'].setValue(LABEL_COLOR)


def create_context_backdrops() -> list[nuke.BackdropNode]:
    backdrops = create_backdrops_for_selected_node()
    for bd in backdrops:
        add_context_knobs(node=bd)
        appearance = get_preferences_node()[
            PREFS_BACKDROP_APPEARANCE_KNOB].value()
        bd['appearance'].setValue(appearance)
        bd.setName(CONTEXT_BACKDROP_NAME)
        _set_context_look(bd)
    return backdrops


def set_context_node(node: nuke.Node):
    node.hideControlPanel()  # Avoid dealing with knob callback
    # and Qt signals.
    for fct in add_context_callbacks:
        fct(node)
    QtCore.QTimer.singleShot(0, lambda: node.showControlPanel())


def clear_context_node(node: nuke.Node):
    node.hideControlPanel()  # Avoid dealing with knob callback
    # and Qt signals.
    for fct in remove_context_callbacks:
        fct(node)
    QtCore.QTimer.singleShot(0, lambda: node.showControlPanel())


def set_context_backdrops_from_selection():
    for group, nodes in get_selected_nodes_by_group().items():
        if not nodes:
            continue
        with group:  # Allow to set backdrops under each groups
            backdrops = [
                n for n in nodes
                if n.Class() == 'BackdropNode' and n.knob(CONTEXT_RULES)]
            if not backdrops:
                backdrops = create_context_backdrops()
            for node in backdrops:
                set_context_node(node)


def set_context_nodes_from_selection():
    for group, nodes in get_selected_nodes_by_group().items():
        nodes = [n for n in nodes if n.Class() != 'BackdropNode']
        if not nodes:
            continue
        with group:  # Allow to set nodes under each groups
            for node in nodes:
                if node.knob(CONTEXT_RULES) is None:
                    add_context_knobs(node=node, force=True)
                    _set_context_look(node)
                set_context_node(node)


def match_rule_value(test_value: str, rule_value: str) -> bool:
    return fnmatch.fnmatch(test_value, rule_value)


def rule_value_split(rule_value: str) -> list[str]:
    rule_values = rule_value.split(context_value_separator)
    return [x.strip() for x in rule_values]


def check_assignation_visibility(node) -> bool:
    rules = get_rules(node)
    if rules is None:
        return False
    gsv_data = _get_graph_scope_variables()
    for rule in rules:
        if not rule['use']:
            continue
        rule_variable, rule_value = rule['context']
        rule_mode = rule['mode']
        gsv_data_variable = gsv_data.get(rule_variable)
        if not gsv_data_variable:
            continue
        rule_values = rule_value_split(rule_value)
        match_found = any(
            match_rule_value(gsv_data_variable, rv) for rv in rule_values)
        if rule_mode == 'include' and not match_found:
            return False
        if rule_mode == 'exclude' and match_found:
            return False
    return True


def update_content(node: nuke.Node | None = None):
    if not is_root_available():  # HACK: check root availibilty to avoid issue
        # on loading .nk file.
        return
    node = node or nuke.thisNode()
    rules = get_knob_value(node, CONTEXT_RULES)
    if not rules:
        return
    enable = check_assignation_visibility(node)
    nodes = (
        get_backdrop_content(node)
        if node.Class() == 'BackdropNode' else [node])
    for n in nodes:
        if 'disable' in n.knobs():
            n.knob('disable').setValue(not enable)
        if n.Class() != 'BackdropNode':
            # Autolabel is not working on * nodes. This is then set here.
            n['autolabel'].setValue(
                "__import__('importlib')"
                ".import_module('contextnodes.nodes').auto_label_node()")
    color = ENABLE_COLOR if enable else DISABLE_COLOR
    node.knob('tile_color').setValue(color)


def switch_visibility():
    for node in get_all_instances():
        update_content(node)


def get_visible_nodes(node_class: str | list[str] | None = None):
    """Get all visible nodes of the given class

    Nodes are included if no rule disables them.
    Nodes outside a context backdrop or without any rule are also included.
    """
    not_visible_nodes = []
    # Filter backdrop context content
    not_visible_multishot_backdrop_nodes = [
        n for n in get_all_instances(node_class='BackdropNode')
        if CONTEXT_RULES in n.knobs()
        and not check_assignation_visibility(n)]
    for bd in not_visible_multishot_backdrop_nodes:
        not_visible_nodes.extend(get_backdrop_content(bd))
    if isinstance(node_class, str):
        node_class = [node_class]
    if node_class is None:
        all_nodes = get_all_instances()
    else:
        all_nodes = []
        for nc in node_class:
            all_nodes.extend(get_all_instances(nc))
    nodes = [n for n in all_nodes if n not in not_visible_nodes]
    # Filter single nodes with CONTEXT_RULES knob
    nodes = [
        n for n in nodes
        if (CONTEXT_RULES in n.knobs() and check_assignation_visibility(n))
        or CONTEXT_RULES not in n.knobs()]
    return nodes


add_context_callbacks = [add_context_from_gsv]
remove_context_callbacks = [remove_context_from_gsv]

if __name__ == '__main__':
    create_context_backdrops()

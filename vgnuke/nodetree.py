import copy
import nuke
from .typing import Node


def get_grid_size() -> None:
    prefs = nuke.toNode('preferences')
    width = int(prefs['GridWidth'].value())
    height = int(prefs['GridHeight'].value())
    return width, height


def get_parent_nodes(node: Node) -> None:
    history = [node.input(i) for i in range(node.inputs()) if node.input(i)]
    parents = []
    for n in history:
        if n in parents:
            continue
        parents.extend(get_parent_nodes(n))
    return list(set(history + parents))


def get_dependent_nodes(node: Node) -> None:
    history = copy.copy(node.dependent())
    children = []
    for n in history:
        if n in children:
            continue
        children.extend(get_dependent_nodes(n))
    return list(set(history + children))


def find_nodes(
        node_class: str,
        group: Node = nuke.root(),
        recurse_groups: bool = False) -> None:
    if recurse_groups:
        all_nodes = nuke.allNodes(group=group, recurseGroups=True)
        return [n for n in all_nodes if n.Class() == node_class]
    else:
        return nuke.allNodes(node_class, group=group)


def get_input_connection(group, name):
    input_nodes = [n for n in group.nodes() if n.Class() == 'Input']
    for node in input_nodes:
        input_name = node.name()
        if input_name.startswith('Input'):
            input_name = input_name[len('Input'):]
        if name == input_name:
            return group.input(int(node['number'].value()))


def get_all_instances(
        node_class: str | None = None,
        group: nuke.Node | None = None,
        exclude_class: str | None = None):
    nodes = []
    group_nodes = (
        group.nodes() if group else nuke.allNodes(recurseGroups=False))
    for node in group_nodes:
        cls = node.Class()
        is_included = (
            (node_class is None or cls == node_class) and
            (exclude_class is None or cls != exclude_class))
        if is_included:
            nodes.append(node)
        if cls == 'Group':
            with node:
                nodes.extend(get_all_instances(
                    node_class, node, exclude_class))
    return nodes

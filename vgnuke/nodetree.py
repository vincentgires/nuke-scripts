import copy
import nuke


def get_grid_size():
    prefs = nuke.toNode('preferences')
    width = int(prefs['GridWidth'].value())
    height = int(prefs['GridHeight'].value())
    return width, height


def get_parent_nodes(node):
    history = [node.input(i) for i in range(node.inputs()) if node.input(i)]
    parents = []
    for n in history:
        if n in parents:
            continue
        parents.extend(get_parent_nodes(n))
    return list(set(history + parents))


def get_dependent_nodes(node):
    history = copy.copy(node.dependent())
    children = []
    for n in history:
        if n in children:
            continue
        children.extend(get_dependent_nodes(n))
    return list(set(history + children))


def find_nodes(node_class, group=nuke.root(), recurse_groups=False):
    if recurse_groups:
        all_nodes = nuke.allNodes(group=group, recurseGroups=True)
        return [n for n in all_nodes if n.Class() == node_class]
    else:
        return nuke.allNodes(node_class, group=group)

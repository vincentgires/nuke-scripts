import nuke
from .view import get_views


def find_top_transform_node(
        node: nuke.Node,
        view: str | None = None) -> nuke.Node | None:

    if node.Class() == 'Input':
        node = node.parent().input(int(node['number'].value()))
        if node is None:
            return

    if node.Class().startswith(('Camera', 'Axis')):
        return node

    if node.Class() == 'Switch':
        active_input = int(node['which'].value())  # BUG: returns float
        input_node = node.input(active_input)
        if input_node is None:
            return
        return find_top_transform_node(input_node, view=view)

    if node.Class() == 'JoinViews':
        viewer = nuke.activeViewer()
        if viewer:
            view = view or viewer.view()
        if view is None:
            view = get_views()[0]
        view_index = get_views().index(view)  # Be carefull here, list of viwes
        # in root node and JoinViews inputs might not match.
        input_node = node.input(view_index)
        if input_node is not None:
            return find_top_transform_node(input_node, view=view)

    for i in range(node.inputs()):
        input_node = node.input(i)
        if input_node is not None:
            parent_camera = find_top_transform_node(input_node, view=view)
            if parent_camera is not None:
                return parent_camera

import os
import nuke

setups = {}
# setups = {
#     'DeepSlice': {
#         'input_name': 'DeepMaskSet',
#         'output_name': 'DeepExpressionDisplay',
#         'group_input_name': 'Input',
#         'group_output_name': 'Output1',
#         'link_nodes': [('AddPicker', 0, 'ExpressionRGB')]
#     }
# }


def find_setup(name) -> str:
    env = os.environ.get('NUKE_SETUPS_PATH')
    if env is None:
        return
    search_paths = [
        os.path.expandvars(os.path.expanduser(p))
        for p in env.split(os.pathsep) if p]
    for base in search_paths:
        if not os.path.isdir(base):
            continue
        for f in os.listdir(base):
            if os.path.splitext(f)[0] == name:
                return os.path.join(base, f)


def insert_setup(
        group_node,
        name: str,
        input_name: str,
        output_name: str,
        group_input_name: str | None = None,
        group_output_name: str | None = None,
        link_nodes: list[tuple[str, int, str]] | None = None):

    if not isinstance(group_node, nuke.Group):
        return

    if (setup_path := find_setup(name)) is None:
        return

    group_node.begin()

    # Clear selection
    for n in nuke.selectedNodes():
        n.setSelected(False)

    # Load setup
    before = set(nuke.allNodes())
    nuke.loadToolset(setup_path)
    after = set(nuke.allNodes())
    new_nodes = list(after - before)
    new_nodes_by_name = {n.name(): n for n in new_nodes}
    all_nodes_by_name = {n.name(): n for n in after}

    # Find input and output by name
    in_node = new_nodes_by_name.get(input_name)
    out_node = new_nodes_by_name.get(output_name)

    if in_node is None:
        group_node.end()
        raise RuntimeError(
            "No in node in the setup: '{}'".format(input_name))

    if out_node is None:
        group_node.end()
        raise RuntimeError(
            "No out node in the setup: '{}'".format(output_name))

    # Connect group input/output
    if group_input_name is not None:
        in_node.setInput(0, all_nodes_by_name.get(group_input_name))

    if group_output_name is not None:
        output_node = all_nodes_by_name.get(group_output_name)
        output_node.setInput(0, out_node)

    # Internal links
    if link_nodes is not None:
        for dst_name, dst_input, src_name in link_nodes:
            dst = all_nodes_by_name.get(dst_name)
            src = all_nodes_by_name.get(src_name)
            if dst is None:
                raise RuntimeError("Link dst can't be found: {}".format(
                    dst_name))
            if src is None:
                raise RuntimeError("Link src can't be found: {}".format(
                    src_name))
            dst.setInput(dst_input, src)

    group_node.end()


if __name__ == '__main__':
    node = nuke.selectedNode()
    insert_setup(
        group_node=node,
        name='DeepSlice',
        input_name='DeepMaskSet',
        output_name='DeepExpressionDisplay',
        group_input_name='Input',
        group_output_name='Output1',
        link_nodes=[('AddPicker', 0, 'ExpressionRGB')])

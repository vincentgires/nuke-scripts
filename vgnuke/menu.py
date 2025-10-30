import os
import nuke
import natsort
from functools import partial
import nukescripts.create


def find_gizmos_from_dir(path: str, exclude_nodes: list | None = None):
    names = []
    for file in sorted(os.listdir(path)):
        name, ext = os.path.splitext(file)
        if exclude_nodes is not None and name in exclude_nodes:
            continue
        if ext == '.gizmo':
            names.append(name)
    return names


def populate_menu(menu: nuke.Menu, names: list):
    for name in natsort.natsorted(names):
        rstripped_name = name.rstrip('0123456789')
        menu.addCommand(
            name=rstripped_name,
            command=partial(
                nukescripts.create.createNodeLocal,
                name, f'name {rstripped_name}'))

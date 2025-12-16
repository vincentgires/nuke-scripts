import nuke
from dynanodes import setups, insert_setup
from qtbinding import QtCore


def fill_group(node: nuke.Node | None = None):
    node = node or nuke.thisNode()
    QtCore.QTimer.singleShot(
        0, lambda: insert_setup(node, node.Class(), **setups[node.Class()]))


def sync_on_load():
    for node_class, cfg in setups.items():
        for node in nuke.allNodes(node_class):
            insert_setup(node, node_class, **cfg)


for node_class in setups.keys():
    nuke.addOnCreate(fill_group, nodeClass=node_class)

# NOTE: this is not working on startup (for renderfarm usage)
# TODO: find a way to fill nodes at script load correctly
# nuke.addOnScriptLoad(sync_on_load)

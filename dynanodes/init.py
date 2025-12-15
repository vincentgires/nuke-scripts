import nuke
from dynanodes import setups, insert_setup
from qtbinding import QtCore


def fill_group(node: nuke.Node | None = None):
    node = node or nuke.thisNode()
    QtCore.QTimer.singleShot(
        0, lambda: insert_setup(node, node.Class(), **setups[node.Class()]))


for node_class in setups.keys():
    nuke.addOnCreate(fill_group, nodeClass=node_class)

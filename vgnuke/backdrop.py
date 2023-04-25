import nuke


def get_content(backdrop_node):
    """Return the nodes contained in the backdrop

    node.getNodes() can not be used because it is not supported with the
    terminal mode of Nuke."""

    left = backdrop_node.xpos()
    top = backdrop_node.ypos()
    right = left + backdrop_node.knob('bdwidth').value()
    bottom = top + backdrop_node.knob('bdheight').value()
    nodes = []
    for node in nuke.allNodes():
        x = node.xpos()
        y = node.ypos()
        # BUG: node.screenWidth/node.screenHeight doesn't work in terminal mode
        # and node.width/node.height gives wrong result
        if nuke.GUI:
            width, height = node.screenWidth(), node.screenHeight()
        else:
            # NOTE: Not perfect, node size can be different if label or other
            # setting is changed and makes the node bigger
            width, height = 80, 18
        if x > left and x + width < right and y > top and y + height < bottom:
            nodes.append(node)
    return nodes

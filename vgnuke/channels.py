import nuke


def get_available_layers(node, prefix):
    """Get all available layers in the image"""

    # Connect a deepToImage to get channels
    # Not working with deep image
    deeptoimage = nuke.nodes.DeepToImage()
    deeptoimage.setInput(0, node)
    channels = deeptoimage.channels()
    nuke.delete(deeptoimage)

    # Keep only the channel name without extension
    layers = list(
        set([c.split('.')[0] for c in channels if c.startswith(prefix)]))
    layers.sort()
    return layers

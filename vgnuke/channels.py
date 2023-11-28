from typing import Optional
import nuke
from .typing import Node


def get_available_channels(
        node: Node,
        prefix: Optional[str] = None,
        keep_ext: bool = False) -> list:
    """Get all available channels"""

    # Connect a deepToImage to get channels
    # Not working with deep image
    deeptoimage = nuke.nodes.DeepToImage()
    deeptoimage.setInput(0, node)
    channels = deeptoimage.channels()
    nuke.delete(deeptoimage)

    # Keep only the channel name without extension
    result = list(set([c if keep_ext else c.split('.')[0] for c in channels]))
    if prefix is not None:
        result = [c for c in result if c.startswith(prefix)]
    result.sort()
    return result

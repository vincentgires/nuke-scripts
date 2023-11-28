import nuke
from typing import Union


def set_views(view_names: Union[str, list]) -> None:
    root = nuke.root()
    views = nuke.views()
    if isinstance(view_names, str):
        view_names = [view_names]
    for view in view_names:
        if view not in views:
            root.addView(view)
    # Delete original views after new ones are created because nuke cannot have
    # none.
    for v in views:
        if v not in view_names:
            root.deleteView(v)

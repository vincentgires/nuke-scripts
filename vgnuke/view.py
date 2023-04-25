import nuke


def set_views(view_names):
    root = nuke.root()
    views = nuke.views()
    for view in view_names:
        if view not in views:
            root.addView(view)
    # Delete original views after new ones are created because nuke cannot have
    # none.
    for v in views:
        if v not in view_names:
            root.deleteView(v)

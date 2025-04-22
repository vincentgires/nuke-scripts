import nuke


def is_root_available() -> bool:
    try:
        root = nuke.root()
        if root.name():
            return True
        else:
            return False
    except ValueError:
        return False
